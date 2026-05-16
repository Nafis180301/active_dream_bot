"""
/start command handler and access request flow.
Handles the permission-based entry system.
"""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from database.models import get_user, create_user, set_user_pending
from utils.constants import (
    MSG_WELCOME_NEW, MSG_WELCOME_PENDING, MSG_WELCOME_REJECTED,
    MSG_WELCOME_BANNED, MSG_MAIN_MENU, MSG_ADMIN_ACCESS_REQUEST
)
from utils.keyboards import (
    request_access_keyboard, pending_keyboard, rejected_keyboard,
    main_menu_keyboard, admin_approval_keyboard
)
from config import Config

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    tg_user = update.effective_user
    user = await get_user(tg_user.id)

    if not user:
        # New user — create record and show request access
        await create_user(
            user_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name
        )
        await update.message.reply_text(
            MSG_WELCOME_NEW,
            parse_mode="Markdown",
            reply_markup=request_access_keyboard()
        )
        return

    status = user["status"]

    if status == "approved":
        # Approved user — show main menu
        name = tg_user.first_name or tg_user.username or "User"
        balance = user.get("balance", 0.0)
        await update.message.reply_text(
            MSG_MAIN_MENU.format(name=name, balance=balance),
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    elif status == "pending":
        await update.message.reply_text(
            MSG_WELCOME_PENDING,
            parse_mode="Markdown",
            reply_markup=pending_keyboard()
        )
    elif status == "rejected":
        await update.message.reply_text(
            MSG_WELCOME_REJECTED,
            parse_mode="Markdown",
            reply_markup=rejected_keyboard()
        )
    elif status == "banned":
        await update.message.reply_text(
            MSG_WELCOME_BANNED,
            parse_mode="Markdown"
        )
    else:
        # new status (hasn't requested yet)
        await update.message.reply_text(
            MSG_WELCOME_NEW,
            parse_mode="Markdown",
            reply_markup=request_access_keyboard()
        )


async def request_access_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the 'Request Access' button press."""
    query = update.callback_query
    await query.answer()

    tg_user = query.from_user

    # Update user status to pending
    await set_user_pending(
        user_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name
    )

    # Notify user
    await query.edit_message_text(
        MSG_WELCOME_PENDING,
        parse_mode="Markdown",
        reply_markup=pending_keyboard()
    )

    # Notify all admins
    name = f"{tg_user.first_name or ''} {tg_user.last_name or ''}".strip() or "N/A"
    username = tg_user.username or "N/A"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for admin_id in Config.ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=MSG_ADMIN_ACCESS_REQUEST.format(
                    name=name,
                    username=username,
                    user_id=tg_user.id,
                    time=now
                ),
                parse_mode="Markdown",
                reply_markup=admin_approval_keyboard(tg_user.id)
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")


async def check_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the 'Check Status' button press."""
    query = update.callback_query
    await query.answer()

    user = await get_user(query.from_user.id)

    if not user:
        await query.edit_message_text(
            MSG_WELCOME_NEW,
            parse_mode="Markdown",
            reply_markup=request_access_keyboard()
        )
        return

    status = user["status"]
    if status == "approved":
        name = query.from_user.first_name or query.from_user.username or "User"
        balance = user.get("balance", 0.0)
        await query.edit_message_text(
            MSG_MAIN_MENU.format(name=name, balance=balance),
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    elif status == "pending":
        await query.answer("⏳ Your request is still pending. Please wait.", show_alert=True)
    elif status == "rejected":
        await query.edit_message_text(
            MSG_WELCOME_REJECTED,
            parse_mode="Markdown",
            reply_markup=rejected_keyboard()
        )
    elif status == "banned":
        await query.edit_message_text(
            MSG_WELCOME_BANNED,
            parse_mode="Markdown"
        )
