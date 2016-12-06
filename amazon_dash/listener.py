import getpass
import threading
from collections import defaultdict
import time
import logging

import subprocess

import os

from amazon_dash.config import Config
from amazon_dash.exceptions import SecurityException
from amazon_dash.scan import scan


DEFAULT_DELAY = 10
EXECUTE_SHELL_PARAM = '-c'
ROOT_USER = 'root'

last_execution = defaultdict(lambda: 0)
logger = logging.getLogger('amazon-dash')


def get_shell(name):
    if name.startswith('/'):
        return [name]
    return ['/usr/bin/env', name]


def run_as_cmd(cmd, user, shell='bash'):
    return ['sudo', '-s', '--set-home', '-u', user] + get_shell(shell) + [EXECUTE_SHELL_PARAM, cmd]


def check_execution_success(cmd, p):
    stdout, stderr = p.communicate()
    if p.returncode:
        logger.error('%i return code on "%s" command. Stderr: %s', p.returncode, ' '.join(cmd), stderr)


def execute(cmd, cwd=None):
    p = subprocess.Popen(cmd, cwd=cwd, stderr=subprocess.PIPE)
    l = threading.Thread(target=check_execution_success, args=(cmd, p))
    l.daemon = True
    l.start()


class Device(object):
    def __init__(self, device, data=None):
        self.src = getattr(device, 'src', device).lower()
        self.data = data
        self.cmd = data.get('cmd')
        self.user = data.get('user', getpass.getuser())
        self.cwd = data.get('cwd')

    @property
    def name(self):
        return self.data.get('name', self.src)

    def execute(self, root_allowed=False):
        logger.debug('%s device executed (mac %s)', self.name, self.src)
        if not self.cmd:
            logger.warning('%s: There is no cmd in device conf.', self.name)
            return
        cmd = self.cmd
        if self.user == ROOT_USER and not root_allowed:
            raise SecurityException('For security, execution as root is not allowed.')
        cmd = run_as_cmd(cmd, self.user)
        execute(cmd, self.cwd)


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
        scan(self.on_push, lambda d: d.src.lower() in self.devices)
