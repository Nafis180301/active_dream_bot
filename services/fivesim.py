"""
5sim.net SMS API provider implementation.
Documentation: https://5sim.net/docs
"""
import aiohttp
import logging
from services.sms_provider import SmsProvider, NumberResult, SmsResult
from config import Config

logger = logging.getLogger(__name__)


class FiveSimProvider(SmsProvider):
    """5sim.net API implementation."""

    def __init__(self):
        self.api_key = Config.FIVESIM_API_KEY
        self.base_url = Config.FIVESIM_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict | None:
        """Make an API request to 5sim."""
        url = f"{self.base_url}{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=self.headers, **kwargs) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        text = await resp.text()
                        logger.error(f"5sim API error {resp.status}: {text}")
                        return {"error": text, "status_code": resp.status}
        except Exception as e:
            logger.error(f"5sim API request failed: {e}")
            return {"error": str(e)}

    async def get_balance(self) -> float:
        """Get the 5sim account balance."""
        result = await self._request("GET", "/user/profile")
        if result and "balance" in result:
            return float(result["balance"])
        return 0.0

    async def buy_number(self, country: str, service: str) -> NumberResult:
        """
        Buy a virtual phone number.
        
        API: GET /user/buy/activation/{country}/{operator}/{product}
        Using 'any' operator to let 5sim choose the best available.
        """
        endpoint = f"/user/buy/activation/{country}/any/{service}"
        result = await self._request("GET", endpoint)

        if not result or "error" in result:
            error_msg = result.get("error", "Unknown error") if result else "No response"
            return NumberResult(
                success=False,
                error=str(error_msg)
            )

        # Map country to flag emoji
        country_flags = {
            "russia": "🇷🇺", "usa": "🇺🇸", "england": "🇬🇧", "india": "🇮🇳",
            "indonesia": "🇮🇩", "philippines": "🇵🇭", "ethiopia": "🇪🇹",
            "kenya": "🇰🇪", "nigeria": "🇳🇬", "bangladesh": "🇧🇩",
            "pakistan": "🇵🇰", "brazil": "🇧🇷", "egypt": "🇪🇬",
            "vietnam": "🇻🇳", "ukraine": "🇺🇦", "kazakhstan": "🇰🇿",
            "myanmar": "🇲🇲", "colombia": "🇨🇴", "mexico": "🇲🇽",
            "thailand": "🇹🇭",
        }

        phone = result.get("phone", "")
        order_id = str(result.get("id", ""))
        cost = float(result.get("price", 0))
        country_name = result.get("country", country).title()
        flag = country_flags.get(country, "🌍")

        return NumberResult(
            success=True,
            order_id=order_id,
            phone_number=phone,
            country=country_name,
            country_code=flag,
            service=service,
            cost=cost,
        )

    async def check_sms(self, order_id: str) -> SmsResult:
        """
        Check if SMS has been received.
        
        API: GET /user/check/{order_id}
        
        Status values: PENDING, RECEIVED, CANCELED, TIMEOUT, FINISHED, BANNED
        """
        result = await self._request("GET", f"/user/check/{order_id}")

        if not result or "error" in result:
            return SmsResult(
                received=False,
                status="error",
                error=result.get("error", "Unknown") if result else "No response"
            )

        status = result.get("status", "").upper()
        sms_list = result.get("sms", [])

        if status == "RECEIVED" and sms_list:
            # Extract the OTP code from the SMS
            latest_sms = sms_list[-1]
            code = latest_sms.get("code", "")
            full_text = latest_sms.get("text", "")
            return SmsResult(
                received=True,
                code=code,
                full_text=full_text,
                status="received",
            )
        elif status in ("CANCELED", "TIMEOUT", "BANNED"):
            # Map to status strings that poll_for_otp expects
            status_map = {
                "CANCELED": "cancelled",
                "TIMEOUT": "expired",
                "BANNED": "cancelled",
            }
            return SmsResult(
                received=False,
                status=status_map.get(status, status.lower()),
            )
        elif status == "FINISHED":
            return SmsResult(
                received=True,
                status="finished",
                code=sms_list[-1].get("code", "") if sms_list else "",
                full_text=sms_list[-1].get("text", "") if sms_list else "",
            )
        else:
            # Still waiting
            return SmsResult(
                received=False,
                status="waiting",
            )

    async def cancel_number(self, order_id: str) -> bool:
        """Cancel a number order."""
        result = await self._request("GET", f"/user/cancel/{order_id}")
        if result and result.get("status", "").upper() == "CANCELED":
            return True
        # Some cases return the order with updated status
        return result is not None and "error" not in result

    async def finish_number(self, order_id: str) -> bool:
        """Mark a number as finished (after receiving OTP)."""
        result = await self._request("GET", f"/user/finish/{order_id}")
        if result and result.get("status", "").upper() == "FINISHED":
            return True
        return result is not None and "error" not in result

    async def get_prices(self, country: str = None, service: str = None) -> dict:
        """
        Get pricing information.
        
        API: GET /guest/prices?country={country}&product={service}
        """
        params = {}
        if country:
            params["country"] = country
        if service:
            params["product"] = service
        
        result = await self._request("GET", "/guest/prices", params=params)
        return result if result else {}
