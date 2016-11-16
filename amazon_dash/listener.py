from amazon_dash.config import Config
from amazon_dash.scan import scan, print_pkt


class Listener(object):
    def __init__(self, config_path):
        self.config = Config(config_path)
        self.mac_devices = list(map(str.lower, self.config['devices'].keys()))

    def on_push(self, device):
        print_pkt(device)

    def run(self):
        scan(self.on_push, lambda d: d.src.lower() in self.mac_devices)
