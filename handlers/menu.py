"""
Main menu and navigation handler.
Handles menu display and back navigation.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from database.models import get_user
from utils.constants import MSG_MAIN_MENU
from utils.keyboards import main_menu_keyboard
from utils.decorators import require_approved

logger = logging.getLogger(__name__)


@require_approved
async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 'Back to Menu' button press."""
    query = update.callback_query
    await query.answer()

    tg_user = query.from_user
    user = await get_user(tg_user.id)
    name = tg_user.first_name or tg_user.username or "User"
    balance = user.get("balance", 0.0) if user else 0.0

    await query.edit_message_text(
        MSG_MAIN_MENU.format(name=name, balance=balance),
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
