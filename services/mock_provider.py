"""
Mock SMS Provider for FREE testing.
Simulates number purchasing and OTP reception without any real API calls.
No account or payment needed.
"""
import random
import asyncio
import logging
from services.sms_provider import SmsProvider, NumberResult, SmsResult

logger = logging.getLogger(__name__)

# Fake phone numbers by country
FAKE_NUMBERS = {
    "russia": "+7",
    "usa": "+1",
    "england": "+44",
    "india": "+91",
    "indonesia": "+62",
    "philippines": "+63",
    "ethiopia": "+251",
    "kenya": "+254",
    "nigeria": "+234",
    "bangladesh": "+880",
    "pakistan": "+92",
    "brazil": "+55",
    "egypt": "+20",
    "vietnam": "+84",
    "ukraine": "+380",
    "kazakhstan": "+7",
    "myanmar": "+95",
    "colombia": "+57",
    "mexico": "+52",
    "thailand": "+66",
}

COUNTRY_FLAGS = {
    "russia": "🇷🇺", "usa": "🇺🇸", "england": "🇬🇧", "india": "🇮🇳",
    "indonesia": "🇮🇩", "philippines": "🇵🇭", "ethiopia": "🇪🇹",
    "kenya": "🇰🇪", "nigeria": "🇳🇬", "bangladesh": "🇧🇩",
    "pakistan": "🇵🇰", "brazil": "🇧🇷", "egypt": "🇪🇬",
    "vietnam": "🇻🇳", "ukraine": "🇺🇦", "kazakhstan": "🇰🇿",
    "myanmar": "🇲🇲", "colombia": "🇨🇴", "mexico": "🇲🇽",
    "thailand": "🇹🇭",
}

# Track mock orders for OTP simulation
_mock_orders: dict[str, dict] = {}
_order_counter = 1000


class MockProvider(SmsProvider):
    """
    Mock SMS provider for testing.
    Simulates the full number + OTP flow with fake data.
    OTP 'arrives' after 10-20 seconds automatically.
    """

    def __init__(self):
        logger.info("🧪 MockProvider initialized — FREE testing mode")

    async def get_balance(self) -> float:
        """Return a fake balance."""
        return 99999.99

    async def buy_number(self, country: str, service: str) -> NumberResult:
        """Generate a fake phone number."""
        global _order_counter
        _order_counter += 1
        order_id = str(_order_counter)

        # Generate a realistic-looking phone number
        prefix = FAKE_NUMBERS.get(country, "+1")
        number = prefix + "".join([str(random.randint(0, 9)) for _ in range(10 - len(prefix) + 1)])
        flag = COUNTRY_FLAGS.get(country, "🌍")

        # Store the order for OTP simulation
        _mock_orders[order_id] = {
            "phone": number,
            "country": country.title(),
            "flag": flag,
            "service": service,
            "created": asyncio.get_running_loop().time(),
            "otp_delay": random.randint(8, 20),  # OTP arrives after 8-20 seconds
            "otp_code": str(random.randint(100000, 999999)),  # 6-digit OTP
            "status": "waiting",
        }

        logger.info(f"🧪 MOCK: Bought number {number} (order {order_id}) for {service}/{country}")

        return NumberResult(
            success=True,
            order_id=order_id,
            phone_number=number,
            country=country.title(),
            country_code=flag,
            service=service,
            cost=0.0,  # Free in mock mode!
        )

    async def check_sms(self, order_id: str) -> SmsResult:
        """Check if the fake OTP has 'arrived'."""
        order = _mock_orders.get(order_id)
        if not order:
            return SmsResult(received=False, status="error", error="Order not found")

        if order["status"] in ("cancelled", "finished"):
            return SmsResult(received=False, status=order["status"])

        # Check if enough time has passed for the OTP to "arrive"
        elapsed = asyncio.get_running_loop().time() - order["created"]

        if elapsed >= order["otp_delay"]:
            # OTP has "arrived"!
            code = order["otp_code"]
            service = order["service"].title()
            sms_text = f"Your {service} verification code is: {code}. Don't share this code with anyone."
            order["status"] = "received"

            logger.info(f"🧪 MOCK: OTP received for order {order_id}: {code}")

            return SmsResult(
                received=True,
                code=code,
                full_text=sms_text,
                status="received",
            )
        else:
            # Still waiting
            remaining = int(order["otp_delay"] - elapsed)
            logger.info(f"🧪 MOCK: Waiting for OTP (order {order_id}), ~{remaining}s remaining")
            return SmsResult(received=False, status="waiting")

    async def cancel_number(self, order_id: str) -> bool:
        """Cancel a mock order."""
        if order_id in _mock_orders:
            _mock_orders[order_id]["status"] = "cancelled"
            logger.info(f"🧪 MOCK: Order {order_id} cancelled")
        return True

    async def finish_number(self, order_id: str) -> bool:
        """Finish a mock order."""
        if order_id in _mock_orders:
            _mock_orders[order_id]["status"] = "finished"
            logger.info(f"🧪 MOCK: Order {order_id} finished")
        return True

    async def get_prices(self, country: str = None, service: str = None) -> dict:
        """Return mock pricing."""
        return {"mock": True, "price": 0.0, "message": "Free testing mode"}
