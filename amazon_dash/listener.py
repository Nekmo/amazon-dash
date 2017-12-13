import time
from collections import defaultdict


from amazon_dash.config import Config
from amazon_dash.exceptions import InvalidConfig
from amazon_dash.execute import logger, ExecuteCmd, ExecuteUrl
from amazon_dash.scan import scan_devices

DEFAULT_DELAY = 10
EXECUTE_CLS = {
    'cmd': ExecuteCmd,
    'url': ExecuteUrl,
}

last_execution = defaultdict(lambda: 0)


class Device(object):
    execute_instance = None

    def __init__(self, src, data=None):
        data = data or {}
        if isinstance(src, Device):
            src = src.src
        self.src = src.lower()
        self.data = data
        execs = [cls(self.name, data) for name, cls in EXECUTE_CLS.items() if name in self.data]
        if len(execs) > 1:
            raise InvalidConfig(
                extra_body='There can only be one method of execution on a device. The device is {}. '.format(self.name)
            )
        elif len(execs):
            self.execute_instance = execs[0]
            self.execute_instance.validate()

    @property
    def name(self):
        return self.data.get('name', self.src)

    def execute(self, root_allowed=False):
        logger.debug('%s device executed (mac %s)', self.name, self.src)
        if not self.execute_instance:
            logger.warning('%s: There is not execution method in device conf.', self.name)
            return
        self.execute_instance.execute(root_allowed)


class Listener(object):
    root_allowed = False

    def __init__(self, config_path):
        self.config = Config(config_path)
        self.settings = self.config.get('settings', {})
        self.devices = {key.lower(): Device(key, value) for key, value in self.config['devices'].items()}
        assert len(self.devices) == len(self.config['devices']), "Duplicate(s) MAC(s) on devices config."

    def on_push(self, device):
        src = device.src.lower()
        if last_execution[src] + self.settings.get('delay', DEFAULT_DELAY) > time.time():
            return
        last_execution[src] = time.time()
        self.execute(device)

    def execute(self, device):
        src = device.src.lower()
        device = self.devices[src]
        device.execute(root_allowed=self.root_allowed)

    def run(self, root_allowed=False):
        self.root_allowed = root_allowed
        scan_devices(self.on_push, lambda d: d.src.lower() in self.devices)
