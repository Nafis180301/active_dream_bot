"""
Configuration loader for Active Dream Bot.
Reads settings from .env file.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = [
        int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    ]

    # 5sim.net API
    FIVESIM_API_KEY: str = os.getenv("FIVESIM_API_KEY", "")
    FIVESIM_BASE_URL: str = "https://5sim.net/v1"

    # OTP Group & Channel
    OTP_GROUP_ID: int = int(os.getenv("OTP_GROUP_ID", "0"))
    OTP_GROUP_LINK: str = os.getenv("OTP_GROUP_LINK", "https://t.me/ActiveDreamOTP")
    CHANNEL_LINK: str = os.getenv("CHANNEL_LINK", "https://t.me/ActiveDreamChannel")

    # Bot Settings
    BOT_NAME: str = os.getenv("BOT_NAME", "Active Dream")
    OTP_CHECK_INTERVAL: int = int(os.getenv("OTP_CHECK_INTERVAL", "5"))
    OTP_MAX_WAIT: int = int(os.getenv("OTP_MAX_WAIT", "300"))

    @classmethod
    def validate(cls) -> list[str]:
        """Validate that required configuration values are set."""
        errors = []
        if not cls.BOT_TOKEN or cls.BOT_TOKEN == "your_bot_token_here":
            errors.append("BOT_TOKEN is not set in .env")
        if not cls.ADMIN_IDS:
            errors.append("ADMIN_IDS is not set in .env")
        # 5sim key is optional — bot uses MockProvider for free testing without it
        if not cls.FIVESIM_API_KEY or cls.FIVESIM_API_KEY == "your_5sim_api_key_here":
            import logging
            logging.getLogger(__name__).warning(
                "⚠️ FIVESIM_API_KEY not set — running in FREE TEST MODE (mock numbers)"
            )
        return errors

