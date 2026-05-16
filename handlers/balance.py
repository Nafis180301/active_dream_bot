"""
Balance and transaction handlers.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from database.models import get_balance, get_transactions
from utils.constants import MSG_BALANCE, MSG_WITHDRAW_INFO
from utils.keyboards import back_to_menu_keyboard
from utils.decorators import require_approved

logger = logging.getLogger(__name__)


@require_approved
async def balance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show balance and recent transactions."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    balance = await get_balance(user_id)
    txs = await get_transactions(user_id, limit=5)
    if txs:
        tx_lines = []
        for tx in txs:
            emoji = "➕" if tx["amount"] > 0 else "➖"
            tx_lines.append(f"{emoji} ${abs(tx['amount']):.2f} — _{tx['type']}_ ({tx['created_at'][:10]})")
        transactions_text = "\n".join(tx_lines)
    else:
        transactions_text = "_No transactions yet._"
    await query.edit_message_text(
        MSG_BALANCE.format(balance=balance, transactions=transactions_text),
        parse_mode="Markdown", reply_markup=back_to_menu_keyboard()
    )


@require_approved
async def withdraw_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 'Withdraw' button."""
    query = update.callback_query
    await query.answer()
    balance = await get_balance(query.from_user.id)
    await query.edit_message_text(
        MSG_WITHDRAW_INFO.format(balance=balance),
        parse_mode="Markdown", reply_markup=back_to_menu_keyboard()
    )
