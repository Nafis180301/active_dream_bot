"""
Abstract SMS Provider interface.
Implement this interface to add support for different SMS API providers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class NumberResult:
    """Result of buying a phone number."""
    success: bool
    order_id: str = ""
    phone_number: str = ""
    country: str = ""
    country_code: str = ""  # flag emoji
    service: str = ""
    cost: float = 0.0
    error: str = ""


@dataclass
class SmsResult:
    """Result of checking for an SMS."""
    received: bool
    code: str = ""
    full_text: str = ""
    status: str = ""  # waiting, received, cancelled, expired
    error: str = ""


class SmsProvider(ABC):
    """Abstract base class for SMS API providers."""

    @abstractmethod
    async def get_balance(self) -> float:
        """Get the API account balance."""
        pass

    @abstractmethod
    async def buy_number(self, country: str, service: str) -> NumberResult:
        """Buy a virtual phone number for the given service and country."""
        pass

    @abstractmethod
    async def check_sms(self, order_id: str) -> SmsResult:
        """Check if an SMS has been received for the given order."""
        pass

    @abstractmethod
    async def cancel_number(self, order_id: str) -> bool:
        """Cancel/release a phone number order."""
        pass

    @abstractmethod
    async def finish_number(self, order_id: str) -> bool:
        """Mark a number order as finished (after receiving OTP)."""
        pass

    @abstractmethod
    async def get_prices(self, country: str = None, service: str = None) -> dict:
        """Get pricing information."""
        pass
