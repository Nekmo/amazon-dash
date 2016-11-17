import threading
from collections import defaultdict
import time
import logging

import subprocess

import os

from amazon_dash.config import Config
from amazon_dash.scan import scan, print_pkt


DEFAULT_DELAY = 10

last_execution = defaultdict(lambda: 0)
logger = logging.getLogger('amazon-dash')


def run_as_cmd(cmd, user):
    if os.getuid():
        # Is't root
        return cmd
    return 'sudo -s --set-home -u {} {}'.format(user, cmd)


def check_execution_success(cmd, p):
    stdout, stderr = p.communicate()
    if p.returncode:
        logger.error('%i return code on "%s" command. Stderr: %s', p.returncode, cmd, stderr)


def execute(cmd, cwd=None):
    p = subprocess.Popen(cmd, shell=True, cwd=cwd, stderr=subprocess.PIPE)
    l = threading.Thread(target=check_execution_success, args=(cmd, p))
    l.daemon = True
    l.start()


class Device(object):
    def __init__(self, device, data=None):
        self.src = getattr(device, 'src', device).lower()
        self.data = data
        self.cmd = data.get('cmd')
        self.user = data.get('user')
        self.cwd = data.get('cwd')

    @property
    def name(self):
        return self.data.get('name', self.src)

    def execute(self):
        logger.debug('%s device executed (mac %s)', self.name, self.src)
        if not self.cmd:
            logger.warning('%s: There is no cmd in device conf.', self.name)
            return
        cmd = self.cmd
        if self.user:
            cmd = run_as_cmd(cmd, self.user)
        execute(cmd, self.cwd)


class Listener(object):
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
        device.execute()

    def run(self):
        scan(self.on_push, lambda d: d.src.lower() in self.devices)
