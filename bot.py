"""
Active Dream Bot — Main Entry Point
Permission-based private Telegram OTP/Virtual Number bot.

Usage:
    1. Copy .env.example to .env and fill in your values
    2. pip install -r requirements.txt
    3. python bot.py
"""
import logging
import sys
import os

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from config import Config
from database.db import init_db, close_db
from handlers.start import start_command, request_access_callback, check_status_callback
from handlers.menu import back_to_menu_callback
from handlers.numbers import (
    get_number_callback, service_selected_callback,
    country_selected_callback, delete_number_callback,
    active_numbers_callback
)
from handlers.balance import balance_callback, withdraw_callback
from handlers.admin import (
    admin_command, admin_refresh_callback,
    admin_approve_callback, admin_reject_callback,
    admin_pending_callback, admin_users_callback,
    admin_add_balance_callback, addbal_command,
    broadcast_command, ban_command, unban_command
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Called after the application is initialized."""
    await init_db()
    logger.info("✅ Bot initialized. Database ready.")
    # Notify admins
    for admin_id in Config.ADMIN_IDS:
        try:
            await application.bot.send_message(
                chat_id=admin_id,
                text=f"🤖 *{Config.BOT_NAME}* is now online! ✅",
                parse_mode="Markdown"
            )
        except Exception:
            pass


async def post_shutdown(application: Application) -> None:
    """Called when the application shuts down."""
    await close_db()
    logger.info("🔴 Bot shut down. Database closed.")


def main() -> None:
    """Start the bot."""
    # Validate configuration
    errors = Config.validate()
    if errors:
        print("[ERROR] Configuration errors:")
        for err in errors:
            print(f"   - {err}")
        print("\nPlease fix the .env file and try again.")
        sys.exit(1)

    # Build application
    app = Application.builder().token(Config.BOT_TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()

    # ── Command Handlers ─────────────────────────────────────
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("addbal", addbal_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("unban", unban_command))

    # ── Callback Query Handlers ──────────────────────────────
    # Access request flow
    app.add_handler(CallbackQueryHandler(request_access_callback, pattern="^request_access$"))
    app.add_handler(CallbackQueryHandler(check_status_callback, pattern="^check_status$"))

    # Main menu navigation
    app.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_menu$"))

    # Number flow
    app.add_handler(CallbackQueryHandler(get_number_callback, pattern="^get_number$"))
    app.add_handler(CallbackQueryHandler(service_selected_callback, pattern=r"^svc_"))
    app.add_handler(CallbackQueryHandler(country_selected_callback, pattern=r"^country_"))
    app.add_handler(CallbackQueryHandler(delete_number_callback, pattern=r"^delete_num_"))
    app.add_handler(CallbackQueryHandler(active_numbers_callback, pattern="^active_numbers$"))

    # Balance
    app.add_handler(CallbackQueryHandler(balance_callback, pattern="^balance$"))
    app.add_handler(CallbackQueryHandler(withdraw_callback, pattern="^withdraw$"))

    # Admin callbacks
    app.add_handler(CallbackQueryHandler(admin_approve_callback, pattern=r"^admin_approve_"))
    app.add_handler(CallbackQueryHandler(admin_reject_callback, pattern=r"^admin_reject_"))
    app.add_handler(CallbackQueryHandler(admin_pending_callback, pattern="^admin_pending$"))
    app.add_handler(CallbackQueryHandler(admin_users_callback, pattern="^admin_users$"))
    app.add_handler(CallbackQueryHandler(admin_add_balance_callback, pattern="^admin_add_balance$"))
    app.add_handler(CallbackQueryHandler(admin_refresh_callback, pattern="^admin_refresh$"))

    # Start polling
    print(f"[BOT] {Config.BOT_NAME} is starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
