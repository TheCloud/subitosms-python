# SubitoSMS per Python

Client Python leggero e senza dipendenze per il [gateway HTTP di SubitoSMS](https://www.subitosms.it/gateway_sms_http.php).

## Installazione

```bash
pip install subitosms
```

## Invio di un SMS

```python
from subitosms import Client

sms = Client("la-tua-username", "la-tua-password")
shipment_id = sms.send("MIOBRAND", "+393351234567", "Ciao da SubitoSMS!")
print(f"Spedizione: {shipment_id}")
```

### Più destinatari, invio di prova e ritardato

```python
shipment_id = sms.send(
    "MIOBRAND",
    ["+393351234567", "+393331234567"],
    "Promemoria appuntamento domani alle 10:00.",
    test=True,
    delay_minutes=15,
)
```

## Credito e stato della spedizione

```python
credit = sms.balance()
credit_with_foreign = sms.balance(include_foreign=True)

for delivery in sms.status(shipment_id):
    print(delivery.destination, delivery.status, delivery.description)
```

## Gestione degli errori

```python
from subitosms import ApiError, TransportError

try:
    sms.send("MIOBRAND", "+393351234567", "Ciao")
except TransportError:
    # Problema di rete/HTTPS: l'invio potrebbe essere arrivato al gateway.
    pass
except ApiError:
    # Risposta del gateway non valida o non accettata.
    pass
```

Non ritentare automaticamente un invio quando non sai se il gateway lo abbia ricevuto: potresti inviare un SMS duplicato. Conserva l'ID della spedizione e usa `status()` o la callback per seguirne la consegna.

## Licenza

MIT. Vedi [LICENSE](LICENSE).

