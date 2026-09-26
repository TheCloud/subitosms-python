"""Eccezioni del client SubitoSMS."""


class ApiError(Exception):
    """Il gateway ha restituito una risposta non valida o non accettata."""


class TransportError(Exception):
    """Non è stato possibile raggiungere il gateway SubitoSMS."""

