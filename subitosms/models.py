"""Modelli restituiti dal client SubitoSMS."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DeliveryStatus:
    """Stato di consegna di un destinatario."""

    destination: str
    status: int
    description: str

    @property
    def is_terminal(self) -> bool:
        """Indica se non sono previsti ulteriori aggiornamenti di stato."""
        return self.status in {-100, -50, 1, 16}

