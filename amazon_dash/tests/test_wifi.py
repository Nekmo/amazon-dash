import unittest
from unittest.mock import patch

import requests_mock

from amazon_dash.exceptions import ConfigWifiError
from amazon_dash.wifi import Wifi, NetworkManagerWifi, ConfigureAmazonDash, CONFIGURE_URL

DEVICES_OUTPUT = """
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: enp4s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 11:22:33:44:55:66 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.2/24 brd 192.168.1.255 scope global dynamic noprefixroute enp4s0
       valid_lft 1035sec preferred_lft 885sec
    inet6 aaaa::bbbb:cccc:dddd:eeee/64 scope link 
       valid_lft forever preferred_lft forever
"""
WIRELESS_DEVICES_OUTPUT = """
3: wlp2s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 11:22:33:44:55:66 brd ff:ff:ff:ff:ff:ff
    inet 192.168.2.2/24 brd 192.168.2.255 scope global dynamic noprefixroute wlp2s0
       valid_lft 931sec preferred_lft 931sec
    inet6 aaaa::bbbb:cccc:dddd:eeee/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
"""
AMAZON_DASH_RESPONSE = """
<tr class="row">
<th>Serial Number</th>
<td>G010M80234000000</td>
</tr>
<tr class="row">
<th>MAC Address</th>
<td>AABBCCDDEEFF</td>
</tr>
<tr class="row">
<th>Firmware</th>
<td>30017420_EU</td>
</tr>
<tr class="row">
<th>Battery</th>
<td>30</td>
</tr>
"""
NETWORKS_RESPONSE = {
   "amzn_devid":"G010M80234000000",
   "amzn_macid":"",
   "international":1,
   "amzn_networks":[
      {
         "ssid":"wifi-eggs",
         "bssid":"",
         "security":"WPA AES PSK",
         "rssi":"-92"
      }
   ],
   "schemes":[
      0
   ]
}


class TestWifi(unittest.TestCase):
    @patch('amazon_dash.wifi.get_cmd_output',
           return_value=DEVICES_OUTPUT.split('\n') + WIRELESS_DEVICES_OUTPUT.split('\n'))
    def test_get_wireless_devices(self, m):
        w = Wifi()
        self.assertEqual(w.device, 'wlp2s0')

    @patch('amazon_dash.wifi.get_cmd_output', return_value=DEVICES_OUTPUT.split('\n'))
    def test_no_wifi_devices(self, m):
        with self.assertRaises(ConfigWifiError):
            Wifi()
        m.assert_called_once()

    @patch('amazon_dash.wifi.get_cmd_output')
    @patch('amazon_dash.wifi.Wifi.get_network_state', return_value='up')
    def test_connect(self, m1, m2):
        device = 'wifi-eggs'
        essid = 'foo'
        key = 'bar'
        wifi = Wifi(device)
        wifi.connect(essid, key)
        m2.assert_called_once_with(['iwconfig', device, 'essid', essid, 'key', key])
        m1.assert_called_once()

    @patch('amazon_dash.wifi.get_cmd_output')
    def test_dhcp(self, m):
        device = 'wifi-eggs'
        wifi = Wifi(device)
        wifi.dhcp()
        m.assert_called_once_with(['dhclient', device])

    @patch('amazon_dash.wifi.Wifi.get_network_state', return_value='down')
    @patch('amazon_dash.wifi.time.sleep')
    def test_wait_up_timeout(self, m1, m2):
        wifi = Wifi('wifi-eggs')
        with self.assertRaises(ConfigWifiError):
            wifi.wait_up()


class TestNetworkManagerWifi(unittest.TestCase):
    @patch('amazon_dash.wifi.get_cmd_output')
    def test_connect(self, m):
        device = 'wifi-eggs'
        essid = 'foo'
        key = 'bar'
        wifi = NetworkManagerWifi(device)
        wifi.connect(essid, key)
        m.assert_called_once_with(['nmcli', 'device', 'wifi', 'connect', essid, 'password', key])


class TestConfigureAmazonDash(unittest.TestCase):
    def test_get_info(self):
        with requests_mock.mock() as m:
            m.get(CONFIGURE_URL, text=AMAZON_DASH_RESPONSE)
            self.assertEqual(ConfigureAmazonDash().get_info(), {
                'serial_number': 'G010M80234000000',
                'mac_address': 'AABBCCDDEEFF',
                'firmware': '30017420_EU',
                'battery': '30',
            })

    def test_get_networks_availables(self):
        with requests_mock.mock() as m:
            m.get(CONFIGURE_URL, json=NETWORKS_RESPONSE,
                  headers={'Content-Type': 'application/json'})
            self.assertEqual(list(ConfigureAmazonDash().get_networks_availables()),
                             NETWORKS_RESPONSE['amzn_networks'])

    @requests_mock.mock()
    def test_configure_error(self, m):
        m.get(CONFIGURE_URL, json=NETWORKS_RESPONSE,
              headers={'Content-Type': 'application/json'})

        with self.assertRaises(ConfigWifiError):
            ConfigureAmazonDash().configure('foo', 'bar')

    @requests_mock.mock()
    def test_configure(self, m):
        amzn_ssid = 'wifi-eggs'
        amzn_pw = 'bar'
        m.get(CONFIGURE_URL, json=NETWORKS_RESPONSE,
              headers={'Content-Type': 'application/json'})
        m.get(CONFIGURE_URL + '?amzn_ssid={}&amzn_pw={}'.format(amzn_ssid, amzn_pw),
              json=NETWORKS_RESPONSE)
        ConfigureAmazonDash().configure(amzn_ssid, amzn_pw)
