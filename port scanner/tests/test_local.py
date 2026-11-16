import socket
import unittest
from unittest.mock import patch

from port_scanner import get_open_ports


class ScannerTests(unittest.TestCase):
    def fake_socket(self, open_ports):
        factory = patch("port_scanner.socket.socket").start()
        self.addCleanup(patch.stopall)
        connection = factory.return_value.__enter__.return_value
        connection.connect_ex.side_effect = lambda address: 0 if address[1] in open_ports else 111
        return connection

    @patch("port_scanner.socket.gethostbyname", return_value="45.33.32.156")
    def test_inclusive_range_and_list(self, resolve):
        connection = self.fake_socket({20, 22, 80})
        self.assertEqual(get_open_ports("scanme.nmap.org", [20, 80]), [20, 22, 80])
        self.assertEqual(connection.connect_ex.call_count, 61)

    @patch("port_scanner.socket.gethostbyname", return_value="45.33.32.156")
    def test_verbose_hostname(self, resolve):
        self.fake_socket({22, 80})
        self.assertEqual(get_open_ports("scanme.nmap.org", [20, 80], True),
                         "Open ports for scanme.nmap.org (45.33.32.156)\nPORT     SERVICE\n22       ssh\n80       http")

    @patch("port_scanner.socket.gethostbyaddr", side_effect=socket.herror)
    def test_verbose_ip_without_hostname(self, resolve):
        self.fake_socket({443})
        self.assertEqual(get_open_ports("104.26.10.78", [440, 450], True),
                         "Open ports for 104.26.10.78\nPORT     SERVICE\n443      https")

    @patch("port_scanner.socket.gethostbyaddr", return_value=("hackthissite.org", [], []))
    def test_verbose_ip_with_hostname(self, resolve):
        self.fake_socket({443})
        self.assertEqual(get_open_ports("137.74.187.104", [440, 450], True),
                         "Open ports for hackthissite.org (137.74.187.104)\nPORT     SERVICE\n443      https")

    def test_invalid_ip(self):
        self.assertEqual(get_open_ports("266.255.9.10", [22, 42]), "Error: Invalid IP address")

    @patch("port_scanner.socket.gethostbyname", side_effect=socket.gaierror)
    def test_invalid_hostname(self, resolve):
        self.assertEqual(get_open_ports("invalid.example", [22, 42]), "Error: Invalid hostname")

    def test_invalid_ranges(self):
        for ports in ([0, 80], [80, 20], [1, 65536], [True, 80], [1], "80"):
            with self.subTest(ports=ports), self.assertRaises(ValueError):
                get_open_ports("127.0.0.1", ports)

    def test_no_open_ports(self):
        self.fake_socket(set())
        self.assertEqual(get_open_ports("127.0.0.1", [22, 23]), [])

    @patch("port_scanner.socket.gethostbyname", return_value="127.0.0.1")
    def test_full_url(self, resolve):
        self.fake_socket({80})
        self.assertEqual(get_open_ports("http://localhost/path", [80, 80]), [80])

    @patch("port_scanner.socket.gethostbyaddr", side_effect=socket.herror)
    def test_unknown_service(self, resolve):
        self.fake_socket({54321})
        self.assertTrue(get_open_ports("127.0.0.1", [54321, 54321], True).endswith("54321    unknown"))

    def test_real_local_listener(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen(2)
            port = listener.getsockname()[1]
            self.assertEqual(get_open_ports("127.0.0.1", [port, port]), [port])
        self.assertEqual(get_open_ports("127.0.0.1", [port, port]), [])


if __name__ == "__main__":
    unittest.main()
