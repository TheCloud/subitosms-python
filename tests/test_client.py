import unittest

from subitosms import ApiError, Client


class ClientTest(unittest.TestCase):
    def test_send_builds_expected_parameters(self):
        seen = {}

        def transport(parameters, endpoint, timeout):
            seen.update(parameters)
            return "id:12345"

        client = Client("user", "secret", transport=transport)

        self.assertEqual(
            12345,
            client.send("MIOBRAND", ["+393351234567", "3331234567"], "Ciao", True, 10),
        )
        self.assertEqual(
            {
                "username": "user", "password": "secret", "mitt": "MIOBRAND",
                "dest": "+393351234567,3331234567", "testo": "Ciao", "test": "1", "delay": "10",
            },
            seen,
        )

    def test_parses_delivery_statuses_and_terminal_states(self):
        client = Client(
            "user",
            "secret",
            transport=lambda *_: (
                "dest:+393351234567;stato:1;desc:Ricevuto dal destinatario;\n"
                "dest:+393331234567;stato:8;desc:Spedito;"
            ),
        )

        statuses = client.status(123)
        self.assertEqual(2, len(statuses))
        self.assertEqual("+393351234567", statuses[0].destination)
        self.assertTrue(statuses[0].is_terminal)
        self.assertFalse(statuses[1].is_terminal)

    def test_rejects_gateway_errors(self):
        client = Client("user", "secret", transport=lambda *_: "credito insufficiente")
        with self.assertRaises(ApiError):
            client.send("MIOBRAND", "+393351234567", "Ciao")


if __name__ == "__main__":
    unittest.main()
