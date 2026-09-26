"""Client HTTP per il gateway SubitoSMS."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping
from typing import Optional
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .exceptions import ApiError, TransportError
from .models import DeliveryStatus

Transport = Callable[[Mapping[str, str], str, int], str]


class Client:
    """Client per inviare SMS e consultarne credito e stato."""

    DEFAULT_ENDPOINT = "https://www.subitosms.it/gateway.php"

    def __init__(
        self,
        username: str,
        password: str,
        endpoint: str = DEFAULT_ENDPOINT,
        timeout: int = 30,
        transport: Optional[Transport] = None,
    ) -> None:
        if not username or not password:
            raise ValueError("Username e password sono obbligatori.")
        if timeout < 1:
            raise ValueError("Il timeout deve essere maggiore di zero.")

        self._username = username
        self._password = password
        self._endpoint = endpoint
        self._timeout = timeout
        self._transport = transport or self._post

    def send(
        self,
        sender: str,
        destinations: str | Iterable[str],
        message: str,
        test: bool = False,
        delay_minutes: Optional[int] = None,
    ) -> int:
        """Invia il testo a uno o più destinatari e restituisce l'ID spedizione."""
        if not sender or not message:
            raise ValueError("Mittente e testo sono obbligatori.")
        if delay_minutes is not None and delay_minutes < 0:
            raise ValueError("Il ritardo non può essere negativo.")

        numbers = self._normalize_destinations(destinations)
        parameters = {"mitt": sender, "dest": ",".join(numbers), "testo": message}
        if test:
            parameters["test"] = "1"
        if delay_minutes is not None:
            parameters["delay"] = str(delay_minutes)

        response = self._request(parameters).strip()
        match = re.fullmatch(r"id:([0-9]+)", response, re.IGNORECASE)
        if not match:
            raise ApiError(f"Risposta inattesa del gateway: {response}")
        return int(match.group(1))

    def balance(self, include_foreign: bool = False) -> int:
        """Restituisce il credito residuo, opzionalmente incluso l'estero."""
        response = self._request({"estero": "1"} if include_foreign else {}).strip()
        match = re.fullmatch(r"credito:([0-9]+)", response, re.IGNORECASE)
        if not match:
            raise ApiError(f"Risposta inattesa del gateway: {response}")
        return int(match.group(1))

    def status(self, shipment_id: int) -> list[DeliveryStatus]:
        """Restituisce lo stato di consegna per ogni destinatario della spedizione."""
        if shipment_id < 1:
            raise ValueError("L'ID della spedizione deve essere positivo.")

        response = self._request({"id": str(shipment_id)}).strip()
        statuses: list[DeliveryStatus] = []
        for line in response.splitlines():
            match = re.fullmatch(r"dest:([^;]+);stato:(-?[0-9]+);desc:(.*);?", line.strip(), re.IGNORECASE)
            if not match:
                raise ApiError(f"Riga di stato non valida: {line}")
            statuses.append(DeliveryStatus(match.group(1), int(match.group(2)), match.group(3)))
        if not statuses:
            raise ApiError("Il gateway non ha restituito stati di consegna.")
        return statuses

    def _normalize_destinations(self, destinations: str | Iterable[str]) -> list[str]:
        values = destinations.split(",") if isinstance(destinations, str) else destinations
        numbers = [number.strip() for number in values if number.strip()]
        if not numbers:
            raise ValueError("Indicare almeno un destinatario.")
        for number in numbers:
            if not re.fullmatch(r"\+?[0-9]+", number):
                raise ValueError(f"Destinatario non valido: {number}")
        return numbers

    def _request(self, parameters: Mapping[str, str]) -> str:
        return self._transport(
            {"username": self._username, "password": self._password, **parameters},
            self._endpoint,
            self._timeout,
        )

    @staticmethod
    def _post(parameters: Mapping[str, str], endpoint: str, timeout: int) -> str:
        request = Request(
            endpoint,
            data=urlencode(parameters).encode("utf-8"),
            headers={"Accept": "text/plain", "Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8")
        except (OSError, URLError) as error:
            raise TransportError("Impossibile contattare il gateway SubitoSMS.") from error

