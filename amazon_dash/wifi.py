"""
netstat -i
iwconfig wlan0 essid NETWORK_NAME key WIRELESS_KEY
dhclient wlan0
"""
import subprocess
import sys
import time
from functools import wraps
from subprocess import CalledProcessError

from amazon_dash.exceptions import ConfigWifiError

from bs4 import BeautifulSoup

import requests

CONFIGURE_URL = 'http://192.168.0.1/'

def get_cmd_output(cmd, split_lines=True, decode='utf-8'):
    output = subprocess.check_output(cmd)
    if decode:
        output = output.decode('utf-8')
    if split_lines:
        output = [line.rstrip('\n') for line in output.split('\n')]
    return output


def get_wifi_class():
    try:
        subprocess.check_call(['nmcli', 'general', 'status'])
    except (FileNotFoundError, CalledProcessError):
        return Wifi
    else:
        return NetworkManagerWifi


def retry(exceptions=(Exception,), tries=5):
    def wrap(fn):
        @wraps(fn)
        def f_retry(*args, **kwargs):
            for i in range(1, tries + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    time.sleep(3 * i)
                    if i + 1 >= tries:
                        raise
        return f_retry
    return wrap


class Wifi(object):

    def __init__(self, device=None):
        self.device = device or next(self.get_wireless_devices(), None)
        if self.device is None:
            raise ConfigWifiError('Wireless card is not available.')

    def get_wireless_devices(self):
        devices = get_cmd_output(['ip', 'a'])
        devices = map(lambda x: x.split(' ')[1].rstrip(':'), filter(lambda x: not x.startswith(' ') and x, devices))
        return filter(lambda x: x.startswith('wl'), devices)

    @retry(ConfigWifiError)
    def connect(self, essid, key=None):
        cmd = ['iwconfig', self.device, 'essid', essid]
        if key:
            cmd += ['key', key]
        get_cmd_output(cmd)
        self.wait_up()

    def get_network_state(self):
        return open('/sys/class/net/{}/operstate'.format(self.device)).read().rstrip('\n')

    def wait_up(self, timeout=5):
        for i in range(timeout * 10):
            if self.get_network_state() == 'up':
                return
            time.sleep(.1)
        ConfigWifiError('Timeout connecting to network')

    def dhcp(self):
        get_cmd_output(['dhclient', self.device])


class NetworkManagerWifi(Wifi):
    @retry()
    def connect(self, essid, key=None):
        get_cmd_output(['nmcli', 'device', 'wifi', 'connect', essid])

    def dhcp(self):
        pass


class ConfigureAmazonDash(object):
    def __init__(self):
        pass

    @retry((ConfigWifiError, requests.exceptions.BaseHTTPError))
    def get_info(self):
        r = requests.get(CONFIGURE_URL)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all('td')
        return {
            'serial_number': items[0].string,
            'mac_address': items[1].string,
            'firmware': items[2].string,
            'battery': items[3].string,
        }

    def get_networks_availables(self):
        r = requests.get(CONFIGURE_URL, headers={'Content-Type': 'application/json'}, timeout=5)
        r.raise_for_status()
        data = r.json()
        return iter(data['amzn_networks'])

    def configure(self, ssid, password):
        networks = self.get_networks_availables()
        if not next(filter(lambda x: x['ssid'] == ssid, networks), None):
            raise ConfigWifiError('Network {} is not available.'.format(ssid))
        r = requests.get(CONFIGURE_URL, {'amzn_ssid': ssid, 'amzn_pw': password})
        r.raise_for_status()


def enable_wifi():
    wifi_class = get_wifi_class()
    w = wifi_class()
    essid = 'Amazon ConfigureMe'
    try:
        w.connect(essid)
    except CalledProcessError:
        raise ConfigWifiError('Error connecting to amazon-dash. '
                              'Is the led flashing blue on the amazon-dash button?'.format(essid))
    w.dhcp()
