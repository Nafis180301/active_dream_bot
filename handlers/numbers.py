"""
Number and OTP handlers.
Handles service selection, country selection, number buying, and OTP polling.
"""
import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes

from database.models import (
    get_user, create_number_record, update_number_status,
    get_active_numbers, deduct_balance, add_balance, get_number_by_id
)
from utils.constants import (
    SERVICES, COUNTRIES,
    MSG_SELECT_SERVICE, MSG_SELECT_COUNTRY, MSG_NUMBER_ASSIGNED,
    MSG_OTP_RECEIVED, MSG_NO_OTP, MSG_NO_ACTIVE_NUMBERS,
    MSG_ACTIVE_NUMBERS_HEADER
)
from utils.keyboards import (
    service_selection_keyboard, country_selection_keyboard,
    number_active_keyboard, number_completed_keyboard,
    back_to_menu_keyboard, main_menu_keyboard
)
from utils.decorators import require_approved
from config import Config

logger = logging.getLogger(__name__)

# Auto-select SMS provider: Mock (free testing) or 5sim (production)
_api_key = Config.FIVESIM_API_KEY
if _api_key and _api_key not in ("", "your_5sim_api_key_here"):
    from services.fivesim import FiveSimProvider
    sms_provider = FiveSimProvider()
    logger.info("📡 Using 5sim.net LIVE provider")
else:
    from services.mock_provider import MockProvider
    sms_provider = MockProvider()
    logger.info("🧪 Using FREE Mock provider (no 5sim key set)")


@require_approved
async def get_number_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 'Get Number' button — show service selection."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        MSG_SELECT_SERVICE,
        parse_mode="Markdown",
        reply_markup=service_selection_keyboard()
    )


@require_approved
async def service_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle service selection — show country selection."""
    query = update.callback_query
    await query.answer()

    # Extract service from callback data: svc_facebook -> facebook
    service_key = query.data.replace("svc_", "")
    service_info = SERVICES.get(service_key)

    if not service_info:
        await query.answer("❌ Invalid service selected.", show_alert=True)
        return

    # Store selected service in context
    context.user_data["selected_service"] = service_key

    await query.edit_message_text(
        MSG_SELECT_COUNTRY.format(
            service=service_info["name"],
            emoji=service_info["emoji"]
        ),
        parse_mode="Markdown",
        reply_markup=country_selection_keyboard(service_key)
    )


@require_approved
async def country_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle country selection — buy number and start OTP polling."""
    query = update.callback_query
    await query.answer("🔄 Getting number...")

    tg_user = query.from_user
    user = await get_user(tg_user.id)

    # Extract service and country from callback data: country_facebook_russia
    parts = query.data.replace("country_", "").split("_", 1)
    if len(parts) != 2:
        await query.answer("❌ Invalid selection.", show_alert=True)
        return

    service_key, country_key = parts
    service_info = SERVICES.get(service_key)
    country_info = COUNTRIES.get(country_key)

    if not service_info or not country_info:
        await query.answer("❌ Invalid selection.", show_alert=True)
        return

    # Buy number from 5sim
    await query.edit_message_text(
        f"🔄 *Getting your {service_info['emoji']} {service_info['name']} number from {country_info['flag']} {country_info['name']}...*\n\n"
        f"Please wait...",
        parse_mode="Markdown"
    )

    try:
        result = await sms_provider.buy_number(
            country=country_info["code"],
            service=service_info["code"]
        )
    except Exception as e:
        logger.error(f"Error buying number: {e}")
        await query.edit_message_text(
            f"❌ *Error getting number*\n\n{str(e)}\n\nPlease try again.",
            parse_mode="Markdown",
            reply_markup=back_to_menu_keyboard()
        )
        return

    if not result.success:
        await query.edit_message_text(
            f"❌ *Failed to get number*\n\n"
            f"Error: _{result.error}_\n\n"
            f"This may mean no numbers are available for this service/country.\n"
            f"Try a different country or service.",
            parse_mode="Markdown",
            reply_markup=service_selection_keyboard()
        )
        return

    # Deduct balance
    cost = result.cost
    if cost > 0:
        new_balance = await deduct_balance(
            tg_user.id, cost,
            f"Number purchase: {service_info['name']} - {country_info['name']}"
        )
        if new_balance is None:
            # Insufficient balance — cancel the number
            await sms_provider.cancel_number(result.order_id)
            await query.edit_message_text(
                f"❌ *Insufficient Balance*\n\n"
                f"This number costs *${cost:.2f}* but your balance is *${user['balance']:.2f}*\n\n"
                f"Please add funds to your account.",
                parse_mode="Markdown",
                reply_markup=back_to_menu_keyboard()
            )
            return

    # Save number record
    number_id = await create_number_record(
        user_id=tg_user.id,
        phone_number=result.phone_number,
        country=result.country,
        country_code=result.country_code,
        service=service_info["name"],
        order_id=result.order_id,
        cost=cost
    )

    # Show number assigned message
    await query.edit_message_text(
        MSG_NUMBER_ASSIGNED.format(
            service=service_info["name"],
            number=result.phone_number,
            country=result.country,
            flag=result.country_code,
            interval=Config.OTP_CHECK_INTERVAL,
            max_wait=Config.OTP_MAX_WAIT
        ),
        parse_mode="Markdown",
        reply_markup=number_active_keyboard(number_id)
    )

    # Start OTP polling in the background
    asyncio.create_task(
        poll_for_otp(
            context=context,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            user_id=tg_user.id,
            number_id=number_id,
            order_id=result.order_id,
            phone_number=result.phone_number,
            country=result.country,
            country_code=result.country_code,
            service_name=service_info["name"],
            cost=cost
        )
    )


async def poll_for_otp(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message_id: int,
    user_id: int,
    number_id: int,
    order_id: str,
    phone_number: str,
    country: str,
    country_code: str,
    service_name: str,
    cost: float
) -> None:
    """Poll for OTP in the background."""
    elapsed = 0
    interval = Config.OTP_CHECK_INTERVAL
    max_wait = Config.OTP_MAX_WAIT

    while elapsed < max_wait:
        await asyncio.sleep(interval)
        elapsed += interval

        try:
            result = await sms_provider.check_sms(order_id)
        except Exception as e:
            logger.error(f"Error checking SMS for order {order_id}: {e}")
            continue

        if result.received:
            # OTP received!
            await update_number_status(
                number_id, "completed",
                sms_code=result.code,
                sms_full=result.full_text
            )

            # Finish the order on 5sim
            try:
                await sms_provider.finish_number(order_id)
            except Exception as e:
                logger.error(f"Error finishing order {order_id}: {e}")

            # Update the message
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=MSG_OTP_RECEIVED.format(
                        service=service_name,
                        number=phone_number,
                        country=country,
                        flag=country_code,
                        code=result.code,
                        sms_text=result.full_text or "N/A"
                    ),
                    parse_mode="Markdown",
                    reply_markup=number_completed_keyboard(number_id)
                )
            except Exception as e:
                logger.error(f"Error updating message: {e}")

            # Forward to OTP group
            if Config.OTP_GROUP_ID:
                try:
                    await context.bot.send_message(
                        chat_id=Config.OTP_GROUP_ID,
                        text=(
                            f"🔑 *OTP Received*\n\n"
                            f"📱 *Service:* {service_name}\n"
                            f"📞 *Number:* `{phone_number}`\n"
                            f"🌍 *Country:* {country} {country_code}\n"
                            f"🔑 *Code:* `{result.code}`\n"
                            f"📩 *SMS:* _{result.full_text or 'N/A'}_"
                        ),
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.error(f"Error forwarding OTP to group: {e}")

            return

        elif result.status in ("cancelled", "expired", "error"):
            # Number cancelled/expired
            await update_number_status(number_id, result.status)

            # Refund balance if applicable
            if cost > 0:
                await add_balance(
                    user_id, cost, "refund",
                    f"Refund: Number {phone_number} ({result.status})"
                )

            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=(
                        f"❌ *Number {result.status.title()}*\n\n"
                        f"📱 {service_name} | `{phone_number}` | {country} {country_code}\n\n"
                        f"{'💰 Your balance has been refunded.' if cost > 0 else ''}"
                    ),
                    parse_mode="Markdown",
                    reply_markup=back_to_menu_keyboard()
                )
            except Exception as e:
                logger.error(f"Error updating message: {e}")
            return

    # Timeout — no OTP received
    await update_number_status(number_id, "expired")

    # Cancel on 5sim
    try:
        await sms_provider.cancel_number(order_id)
    except Exception as e:
        logger.error(f"Error cancelling order {order_id}: {e}")

    # Refund balance
    if cost > 0:
        await add_balance(
            user_id, cost, "refund",
            f"Refund: OTP timeout for {phone_number}"
        )

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=MSG_NO_OTP.format(
                service=service_name,
                number=phone_number,
                country=country,
                flag=country_code
            ),
            parse_mode="Markdown",
            reply_markup=back_to_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Error updating timeout message: {e}")


@require_approved
async def delete_number_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 'Delete Number' button."""
    query = update.callback_query
    await query.answer("🗑 Deleting number...")

    # Extract number_id from callback: delete_num_123
    try:
        number_id = int(query.data.replace("delete_num_", ""))
    except ValueError:
        await query.answer("❌ Invalid number.", show_alert=True)
        return

    number = await get_number_by_id(number_id)
    if not number:
        await query.answer("❌ Number not found.", show_alert=True)
        return

    # Cancel on 5sim
    if number["order_id"]:
        try:
            await sms_provider.cancel_number(number["order_id"])
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")

    # Update status
    await update_number_status(number_id, "cancelled")

    # Refund if applicable
    cost = number.get("cost", 0)
    if cost > 0:
        await add_balance(
            number["user_id"], cost, "refund",
            f"Refund: Manually cancelled {number['phone_number']}"
        )

    await query.edit_message_text(
        f"🗑 *Number Deleted*\n\n"
        f"📱 `{number['phone_number']}` has been cancelled.\n"
        f"{'💰 Balance refunded: $' + f'{cost:.2f}' if cost > 0 else ''}",
        parse_mode="Markdown",
        reply_markup=back_to_menu_keyboard()
    )


@require_approved
async def active_numbers_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 'Active Numbers' button."""
    query = update.callback_query
    await query.answer()

    numbers = await get_active_numbers(query.from_user.id)

    if not numbers:
        await query.edit_message_text(
            MSG_NO_ACTIVE_NUMBERS,
            parse_mode="Markdown",
            reply_markup=back_to_menu_keyboard()
        )
        return

    text = MSG_ACTIVE_NUMBERS_HEADER
    for num in numbers:
        status_emoji = "🔄" if num["status"] == "waiting" else "📱"
        text += (
            f"{status_emoji} `{num['phone_number']}` | "
            f"{num['service']} | {num['country']} {num['country_code']}\n"
            f"   Status: *{num['status'].title()}*\n\n"
        )

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=back_to_menu_keyboard()
    )
