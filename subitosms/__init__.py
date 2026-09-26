"""Client Python per le API HTTP di SubitoSMS."""

from .client import Client
from .exceptions import ApiError, TransportError
from .models import DeliveryStatus

__all__ = ["ApiError", "Client", "DeliveryStatus", "TransportError"]

