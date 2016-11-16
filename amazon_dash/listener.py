from collections import defaultdict

import time

from amazon_dash.config import Config
from amazon_dash.scan import scan, print_pkt


last_execution = defaultdict(lambda: 0)


DEFAULT_DELAY = 10

class Listener(object):
    def __init__(self, config_path):
        self.config = Config(config_path)
        self.settings = self.config.get('settings', {})
        self.mac_devices = list(map(str.lower, self.config['devices'].keys()))
        assert len(self.mac_devices) == len(self.config['devices']), "Duplicate(s) MAC(s) on devices config."

    def on_push(self, device):
        if last_execution[device.src] + self.settings.get('delay', DEFAULT_DELAY) > time.time():
            return
        last_execution[device.src] = time.time()
        self.execute(device)
        print_pkt(device)

    def execute(self, device):
        devices = self.config.get('devices', {})
        devices.get()

    def run(self):
        scan(self.on_push, lambda d: d.src.lower() in self.mac_devices)
