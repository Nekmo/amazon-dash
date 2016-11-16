from collections import defaultdict

import time

from amazon_dash.config import Config
from amazon_dash.scan import scan, print_pkt


last_execution = defaultdict(lambda: 0)


class Listener(object):
    def __init__(self, config_path):
        self.config = Config(config_path)
        self.settings = self.config.get('settings', {})
        self.mac_devices = list(map(str.lower, self.config['devices'].keys()))

    def on_push(self, device):
        if last_execution[device.src] + self.settings.get('delay') > time.time():
            return
        last_execution[device.src] = time.time()
        print_pkt(device)

    def run(self):
        scan(self.on_push, lambda d: d.src.lower() in self.mac_devices)
