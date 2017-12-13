import json
import logging
import subprocess
import threading

import getpass

from requests import request, RequestException
from amazon_dash._compat import JSONDecodeError
from amazon_dash.exceptions import SecurityException, InvalidConfig


EXECUTE_SHELL_PARAM = '-c'
ROOT_USER = 'root'

CONTENT_TYPE_METHODS = ['post', 'put', 'patch']
CONTENT_TYPE_ALIASES = {
    'form': 'application/x-www-form-urlencoded',
    'json': 'application/json',
    'plain': 'text/plain',
}

logger = logging.getLogger('amazon-dash')


def get_shell(name):
    if name.startswith('/'):
        return [name]
    return ['/usr/bin/env', name]


def run_as_cmd(cmd, user, shell='bash'):
    return ['sudo', '-s', '--set-home', '-u', user] + get_shell(shell) + [EXECUTE_SHELL_PARAM, cmd]


def check_execution_success(cmd, cwd):
    p = subprocess.Popen(cmd, cwd=cwd, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode:
        logger.error('%i return code on "%s" command. Stderr: %s', p.returncode, ' '.join(cmd), stderr)


def execute_cmd(cmd, cwd=None):
    l = threading.Thread(target=check_execution_success, args=(cmd, cwd))
    l.daemon = True
    l.start()


class Execute(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def validate(self):
        raise NotImplementedError

    def execute(self, root_allowed=False):
        raise NotImplementedError


class ExecuteCmd(Execute):
    def __init__(self, name, data):
        super(ExecuteCmd, self).__init__(name, data)
        self.user = data.get('user', getpass.getuser())
        self.cwd = data.get('cwd')

    def validate(self):
        return

    def execute(self, root_allowed=False):
        if self.user == ROOT_USER and not root_allowed:
            raise SecurityException('For security, execution as root is not allowed.')
        cmd = run_as_cmd(self.data['cmd'], self.user)
        execute_cmd(cmd, self.data.get('cwd'))


class ExecuteUrl(Execute):
    def validate(self):
        if (self.data.get('content-type') or self.data.get('body')) and \
                        self.data.get('method', '').lower() not in CONTENT_TYPE_METHODS:
            raise InvalidConfig(
                extra_body='The body/content-type option only can be used with the {} methods. The device is {}. '
                           'Check the configuration file.'.format(', '.join(CONTENT_TYPE_METHODS), self.name)
            )
        self.data['content-type'] = CONTENT_TYPE_ALIASES.get(self.data.get('content-type'),
                                                             self.data.get('content-type'))
        form_type = CONTENT_TYPE_ALIASES['form']
        if self.data.get('body') and (self.data.get('content-type') or form_type) == form_type:
            try:
                self.data['body'] = json.loads(self.data['body'])
            except JSONDecodeError:
                raise InvalidConfig(
                    extra_body='Invalid JSON body on {} device.'.format(self.name)
                )

    def execute(self, root_allowed=False):
        kwargs = {}
        if self.data.get('content-type'):
            kwargs['headers'] = {'content-type': self.data['content-type']}
        if self.data.get('body'):
            kwargs['data'] = self.data['body']
        try:
            resp = request(self.data.get('method', 'get').lower(), self.data['url'], **kwargs)
        except RequestException as e:
            logger.warning('Exception on request to {}: {}'.format(self.data['url'], e))
            return
        if resp.status_code >= 400:
            logger.warning('"{}" return code {}.'.format(self.data['url'], resp.status_code))
