"""
Inline keyboard layouts for Active Dream Bot.
All keyboard definitions are centralized here.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.constants import SERVICES, COUNTRIES
from config import Config


def request_access_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for new users to request access."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Request Access", callback_data="request_access")],
    ])


def pending_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for users with pending requests."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Check Status", callback_data="check_status")],
    ])


def rejected_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for rejected users to re-request."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Request Access Again", callback_data="request_access")],
    ])


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard for approved users."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 Get Number", callback_data="get_number"),
            InlineKeyboardButton("💰 Balance", callback_data="balance"),
        ],
        [
            InlineKeyboardButton("📊 Active Number", callback_data="active_numbers"),
            InlineKeyboardButton("🤑 Withdraw", callback_data="withdraw"),
        ],
        [
            InlineKeyboardButton("📢 Bot Update Channel", url=Config.CHANNEL_LINK),
        ],
    ])


def service_selection_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting a service (Facebook, etc.)."""
    buttons = []
    row = []
    for key, svc in SERVICES.items():
        row.append(
            InlineKeyboardButton(
                f"{svc['emoji']} {svc['name']}", 
                callback_data=f"svc_{key}"
            )
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")])
    return InlineKeyboardMarkup(buttons)


def country_selection_keyboard(service: str) -> InlineKeyboardMarkup:
    """Keyboard for selecting a country."""
    buttons = []
    row = []
    for key, country in COUNTRIES.items():
        row.append(
            InlineKeyboardButton(
                f"{country['flag']} {country['name']}", 
                callback_data=f"country_{service}_{key}"
            )
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 Back to Services", callback_data="get_number")])
    return InlineKeyboardMarkup(buttons)


def number_active_keyboard(number_id: int) -> InlineKeyboardMarkup:
    """Keyboard shown while waiting for OTP."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🗑 Delete Number", callback_data=f"delete_num_{number_id}"),
            InlineKeyboardButton("📋 Back to Menu", callback_data="back_menu"),
        ],
        [
            InlineKeyboardButton("📱 OTP GROUP HERE", url=Config.OTP_GROUP_LINK),
        ],
    ])


def number_completed_keyboard(number_id: int) -> InlineKeyboardMarkup:
    """Keyboard shown after OTP is received."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 Get Another Number", callback_data="get_number"),
            InlineKeyboardButton("📋 Back to Menu", callback_data="back_menu"),
        ],
        [
            InlineKeyboardButton("📱 OTP GROUP HERE", url=Config.OTP_GROUP_LINK),
        ],
    ])


def admin_approval_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Keyboard for admin to approve/reject a user."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{user_id}"),
        ],
    ])


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Main admin panel keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏳ Pending Requests", callback_data="admin_pending"),
            InlineKeyboardButton("👥 All Users", callback_data="admin_users"),
        ],
        [
            InlineKeyboardButton("💰 Add Balance", callback_data="admin_add_balance"),
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
        ],
        [
            InlineKeyboardButton("🚫 Ban User", callback_data="admin_ban"),
            InlineKeyboardButton("🔓 Unban User", callback_data="admin_unban"),
        ],
        [
            InlineKeyboardButton("🔄 Refresh Stats", callback_data="admin_refresh"),
        ],
    ])


def admin_user_action_keyboard(user_id: int, current_status: str) -> InlineKeyboardMarkup:
    """Admin actions for a specific user."""
    buttons = []
    if current_status != "approved":
        buttons.append(InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_{user_id}"))
    if current_status != "banned":
        buttons.append(InlineKeyboardButton("🚫 Ban", callback_data=f"admin_ban_{user_id}"))
    if current_status == "banned":
        buttons.append(InlineKeyboardButton("🔓 Unban", callback_data=f"admin_approve_{user_id}"))
    
    rows = [buttons] if buttons else []
    rows.append([
        InlineKeyboardButton("💰 Add Balance", callback_data=f"admin_addbal_{user_id}"),
    ])
    rows.append([
        InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel"),
    ])
    return InlineKeyboardMarkup(rows)


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Simple back to menu button."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Back to Menu", callback_data="back_menu")],
    ])


def confirm_keyboard(action: str, target_id: str = "") -> InlineKeyboardMarkup:
    """Confirmation keyboard for destructive actions."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Confirm", callback_data=f"confirm_{action}_{target_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="back_menu"),
        ],
    ])
