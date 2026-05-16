"""
Admin panel handlers.
Approve/reject users, manage balance, broadcast, ban/unban.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from database.models import (
    get_user, update_user_status, get_pending_users, get_all_users,
    get_user_count, add_balance, get_approved_users
)
from database.models import get_number_stats
from utils.constants import MSG_ACCESS_APPROVED, MSG_ADMIN_PANEL
from utils.keyboards import admin_panel_keyboard, admin_user_action_keyboard, back_to_menu_keyboard
from utils.decorators import require_admin
from config import Config

logger = logging.getLogger(__name__)

# Conversation states for admin operations
WAITING_BALANCE_USER_ID, WAITING_BALANCE_AMOUNT = range(2)
WAITING_BROADCAST_MSG = 2
WAITING_BAN_USER_ID = 3
WAITING_UNBAN_USER_ID = 4


@require_admin
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /admin command — show admin panel."""
    user_counts = await get_user_count()
    num_stats = await get_number_stats()
    await update.message.reply_text(
        MSG_ADMIN_PANEL.format(
            total=user_counts.get("total", 0),
            approved=user_counts.get("approved", 0),
            pending=user_counts.get("pending", 0),
            rejected=user_counts.get("rejected", 0),
            banned=user_counts.get("banned", 0),
            num_total=num_stats.get("total", 0),
            num_completed=num_stats.get("completed", 0),
            num_active=num_stats.get("active", 0),
            num_cancelled=num_stats.get("cancelled", 0),
        ),
        parse_mode="Markdown", reply_markup=admin_panel_keyboard()
    )


@require_admin
async def admin_refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Refresh admin panel stats."""
    query = update.callback_query
    await query.answer("🔄 Refreshing...")
    user_counts = await get_user_count()
    num_stats = await get_number_stats()
    await query.edit_message_text(
        MSG_ADMIN_PANEL.format(
            total=user_counts.get("total", 0),
            approved=user_counts.get("approved", 0),
            pending=user_counts.get("pending", 0),
            rejected=user_counts.get("rejected", 0),
            banned=user_counts.get("banned", 0),
            num_total=num_stats.get("total", 0),
            num_completed=num_stats.get("completed", 0),
            num_active=num_stats.get("active", 0),
            num_cancelled=num_stats.get("cancelled", 0),
        ),
        parse_mode="Markdown", reply_markup=admin_panel_keyboard()
    )


@require_admin
async def admin_approve_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Approve a user's access request."""
    query = update.callback_query
    await query.answer("✅ Approving...")
    try:
        target_user_id = int(query.data.replace("admin_approve_", ""))
    except ValueError:
        await query.answer("❌ Invalid user ID.", show_alert=True)
        return
    await update_user_status(target_user_id, "approved", approved_by=query.from_user.id)
    target_user = await get_user(target_user_id)
    name = target_user.get("first_name", "User") if target_user else "User"
    username = target_user.get("username", "N/A") if target_user else "N/A"
    await query.edit_message_text(
        f"✅ *User Approved!*\n\n👤 {name} (@{username})\n🆔 `{target_user_id}`",
        parse_mode="Markdown"
    )
    # Notify the user
    try:
        await context.bot.send_message(
            chat_id=target_user_id, text=MSG_ACCESS_APPROVED, parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {target_user_id}: {e}")


@require_admin
async def admin_reject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reject a user's access request."""
    query = update.callback_query
    await query.answer("❌ Rejecting...")
    try:
        target_user_id = int(query.data.replace("admin_reject_", ""))
    except ValueError:
        await query.answer("❌ Invalid user ID.", show_alert=True)
        return
    await update_user_status(target_user_id, "rejected")
    target_user = await get_user(target_user_id)
    name = target_user.get("first_name", "User") if target_user else "User"
    await query.edit_message_text(
        f"❌ *User Rejected*\n\n👤 {name}\n🆔 `{target_user_id}`",
        parse_mode="Markdown"
    )
    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text="❌ Your access request has been rejected.",
        )
    except Exception as e:
        logger.error(f"Failed to notify user {target_user_id}: {e}")


@require_admin
async def admin_pending_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all pending access requests."""
    query = update.callback_query
    await query.answer()
    pending = await get_pending_users()
    if not pending:
        await query.edit_message_text(
            "✅ *No pending requests!*\n\nAll access requests have been processed.",
            parse_mode="Markdown", reply_markup=admin_panel_keyboard()
        )
        return
    text = f"⏳ *Pending Requests ({len(pending)})*\n\n"
    for u in pending[:20]:
        text += (f"👤 {u.get('first_name', 'N/A')} (@{u.get('username', 'N/A')})\n"
                 f"   🆔 `{u['user_id']}` | 📅 {u['created_at'][:10]}\n\n")
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_panel_keyboard())


@require_admin
async def admin_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all users."""
    query = update.callback_query
    await query.answer()
    users = await get_all_users()
    if not users:
        await query.edit_message_text("No users yet.", reply_markup=admin_panel_keyboard())
        return
    text = f"👥 *All Users ({len(users)})*\n\n"
    status_emojis = {"approved": "✅", "pending": "⏳", "rejected": "❌", "banned": "🚫", "new": "🆕"}
    for u in users[:25]:
        emoji = status_emojis.get(u["status"], "❓")
        text += (f"{emoji} {u.get('first_name', 'N/A')} (@{u.get('username', 'N/A')})\n"
                 f"   🆔 `{u['user_id']}` | 💰 ${u.get('balance', 0):.2f}\n\n")
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_panel_keyboard())


@require_admin
async def admin_add_balance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start add balance flow — ask for user ID."""
    query = update.callback_query
    await query.answer()
    context.user_data["admin_action"] = "add_balance"
    await query.edit_message_text(
        "💰 *Add Balance*\n\nSend the user ID you want to add balance to:\n\n"
        "Format: `/addbal USER_ID AMOUNT`\n"
        "Example: `/addbal 123456789 10.00`",
        parse_mode="Markdown"
    )


@require_admin
async def addbal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /addbal USER_ID AMOUNT command."""
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text(
            "Usage: `/addbal USER_ID AMOUNT`\nExample: `/addbal 123456789 10.00`",
            parse_mode="Markdown"
        )
        return
    try:
        target_id = int(args[0])
        amount = float(args[1])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID or amount.")
        return
    target_user = await get_user(target_id)
    if not target_user:
        await update.message.reply_text("❌ User not found.")
        return
    new_balance = await add_balance(target_id, amount, "admin_add", f"Admin added ${amount:.2f}")
    await update.message.reply_text(
        f"✅ *Balance Added*\n\n👤 {target_user.get('first_name', 'User')}\n"
        f"💰 Added: ${amount:.2f}\n💵 New Balance: ${new_balance:.2f}",
        parse_mode="Markdown"
    )
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=f"💰 *Balance Added!*\n\nAn admin added *${amount:.2f}* to your account.\n"
                 f"💵 New Balance: *${new_balance:.2f}*",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {target_id}: {e}")


@require_admin
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /broadcast MESSAGE command."""
    if not context.args:
        await update.message.reply_text("Usage: `/broadcast Your message here`", parse_mode="Markdown")
        return
    message = " ".join(context.args)
    users = await get_approved_users()
    sent = 0
    failed = 0
    for u in users:
        try:
            await context.bot.send_message(
                chat_id=u["user_id"],
                text=f"📢 *Broadcast from Active Dream*\n\n{message}",
                parse_mode="Markdown"
            )
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(
        f"📢 *Broadcast Complete*\n\n✅ Sent: {sent}\n❌ Failed: {failed}",
        parse_mode="Markdown"
    )


@require_admin
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ban USER_ID command."""
    if not context.args:
        await update.message.reply_text("Usage: `/ban USER_ID`", parse_mode="Markdown")
        return
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return
    await update_user_status(target_id, "banned")
    await update.message.reply_text(f"🚫 User `{target_id}` has been banned.", parse_mode="Markdown")


@require_admin
async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /unban USER_ID command."""
    if not context.args:
        await update.message.reply_text("Usage: `/unban USER_ID`", parse_mode="Markdown")
        return
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return
    await update_user_status(target_id, "approved")
    await update.message.reply_text(f"🔓 User `{target_id}` has been unbanned.", parse_mode="Markdown")
