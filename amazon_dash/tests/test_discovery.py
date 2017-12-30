from __future__ import print_function
import unittest
from amazon_dash.tests._compat import patch

from amazon_dash.discovery import BANNED_DEVICES, pkt_text, AMAZON_DEVICES, mac_id_list, discovery_print, discover
from amazon_dash.listener import Device


class TestDiscovery(unittest.TestCase):
    def test_banned_devices(self):
        banned = Device(BANNED_DEVICES[0])
        self.assertFalse(pkt_text(banned))

    def test_amazon_device(self):
        device = Device(AMAZON_DEVICES[0] + ':00:00:00')
        self.assertIn('Amazon', pkt_text(device))

    def test_device(self):
        device = Device('11:22:33:44:55:66')
        self.assertIn(device.src, pkt_text(device))

    @patch('sys.stdout')
    def test_discovery_print(self, write_patch):
        mac = '11:22:33:44:55:66'
        with patch('amazon_dash.discovery.pkt_text') as pkt_text_mock:
            discovery_print(Device(mac))
            discovery_print(Device(mac))
            pkt_text_mock.assert_called_once()
        mac_id_list.remove(mac)
