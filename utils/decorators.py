"""
Permission decorators for Active Dream Bot.
Used to restrict handler access based on user status.
"""
import functools
from telegram import Update
from telegram.ext import ContextTypes
from database.models import get_user
from config import Config


def require_approved(func):
    """Decorator: Only allow approved users to access the handler."""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        user = await get_user(user_id)
        
        if not user or user["status"] != "approved":
            if update.callback_query:
                await update.callback_query.answer("⚠️ You don't have access. Please request access first.", show_alert=True)
            else:
                await update.message.reply_text("⚠️ You don't have access to this bot. Send /start to request access.")
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapper


def require_admin(func):
    """Decorator: Only allow admin users to access the handler."""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        if user_id not in Config.ADMIN_IDS:
            if update.callback_query:
                await update.callback_query.answer("🚫 Admin access only.", show_alert=True)
            else:
                await update.message.reply_text("🚫 This command is restricted to admins only.")
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapper
