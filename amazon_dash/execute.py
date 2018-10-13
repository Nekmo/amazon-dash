import json
import logging

import getpass

import sys

import copy
from requests import request, RequestException
from amazon_dash._compat import JSONDecodeError
from amazon_dash.exceptions import SecurityException, InvalidConfig, ExecuteError
from ._compat import urlparse, subprocess

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
    """Absolute path to command

    :param str name: command
    :return: command args
    :rtype: list
    """
    if name.startswith('/'):
        return [name]
    return ['/usr/bin/env', name]


def run_as_cmd(cmd, user, shell='bash'):
    """Get the arguments to execute a command as a user

    :param str cmd: command to execute
    :param user: User for use
    :param shell: Bash, zsh, etc.
    :return: arguments
    :rtype: list
    """
    to_execute = get_shell(shell) + [EXECUTE_SHELL_PARAM, cmd]
    if user == 'root':
        return to_execute
    return ['sudo', '-s', '--set-home', '-u', user] + to_execute


def execute_cmd(cmd, cwd=None, timeout=5):
    """Excecute command on thread

    :param cmd: Command to execute
    :param cwd: current working directory
    :return: None
    """
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    else:
        stdout, stderr = p.stdout.read(), p.stderr.read()
        if sys.version_info >= (3,):
            stdout, stderr = stdout.decode('utf-8', errors='ignore'), stderr.decode('utf-8', errors='ignore')
        if p.returncode:
            raise ExecuteError('Error running command {}: The error code {} has returned. Stderr: {}'.format(
                ' '.join(cmd), p.returncode, stderr
            ))
        else:
            return stdout, stderr


def execute_over_ssh(cmd, ssh, cwd=None, shell='bash'):
    """Excecute command on remote machine using SSH

    :param cmd: Command to execute
    :param ssh: Server to connect. Port is optional
    :param cwd: current working directory
    :return: None
    """
    port = None
    parts = ssh.split(':', 1)
    if len(parts) > 1 and not parts[1].isdigit():
        raise InvalidConfig(extra_body='Invalid port number on ssh config: {}'.format(parts[1]))
    elif len(parts) > 1:
        port = parts[1]
    quoted_cmd = ' '.join([x.replace("'", """'"'"'""") for x in cmd.split(' ')])
    remote_cmd = ' '.join([
        ' '.join(get_shell(shell)), # /usr/bin/env bash
        ' '.join([EXECUTE_SHELL_PARAM, "'", ' '.join((['cd', cwd, ';'] if cwd else []) + [quoted_cmd]), "'"])],
    )
    return ['ssh', parts[0]] + (['-p', port] if port else []) + ['-C'] + [remote_cmd]


class Execute(object):
    """Execute base class

    """

    def __init__(self, name, data):
        """

        :param str name: name or mac address
        :param data: data on device section
        """
        self.name = name
        self.data = data

    def validate(self):
        """Check self.data. Raise InvalidConfig on error

        :return: None
        """
        raise NotImplementedError

    def execute(self, root_allowed=False):
        """Execute using self.data

        :param bool root_allowed: Only used for ExecuteCmd
        :return:
        """
        raise NotImplementedError


class ExecuteCmd(Execute):
    """Execute systemd command
    """

    def __init__(self, name, data):
        """

        :param str name: name or mac address
        :param data: data on device section
        """
        super(ExecuteCmd, self).__init__(name, data)
        self.user = data.get('user', getpass.getuser())
        self.cwd = data.get('cwd')

    def validate(self):
        """Check self.data. Raise InvalidConfig on error

        :return: None
        """
        return

    def execute(self, root_allowed=False):
        """Execute using self.data

        :param bool root_allowed: Allow execute as root commands
        :return:
        """
        if self.user == ROOT_USER and not root_allowed and not self.data.get('ssh'):
            raise SecurityException('For security, execute commands as root is not allowed. '
                                    'Use --root-allowed to allow executing commands as root. '
                                    ' It is however recommended to add a user to the configuration '
                                    'of the device (device: {})'.format(self.name))
        if self.data.get('user') and self.data.get('ssh'):
            raise InvalidConfig('User option is unsupported in ssh mode. The ssh user must be defined in '
                                'the ssh option. For example: user@machine')
        if self.data.get('ssh'):
            cmd = execute_over_ssh(self.data['cmd'], self.data['ssh'], self.data.get('cwd'))
            output = execute_cmd(cmd)
        else:
            cmd = run_as_cmd(self.data['cmd'], self.user)
            output = execute_cmd(cmd, self.data.get('cwd'))
        if output:
            return output[0]


class ExecuteUrl(Execute):
    """Call a url
    """

    def validate(self):
        """Check self.data. Raise InvalidConfig on error

        :return: None
        """
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
        """Execute using self.data

        :param bool root_allowed: Only used for ExecuteCmd
        :return:
        """
        kwargs = {'stream': True, 'timeout': 15,
                  'headers': self.data.get('headers', {})}
        if self.data.get('content-type'):
            kwargs['headers']['content-type'] = self.data['content-type']
        if self.data.get('body'):
            kwargs['data'] = self.data['body']
        if self.data.get('auth'):
            kwargs['auth'] = tuple(self.data['auth'].split(':', 1))
        try:
            resp = request(self.data.get('method', 'get').lower(), self.data['url'],
                           verify=self.data.get('verify', True),
                           **kwargs)
        except RequestException as e:
            raise ExecuteError('Exception on request to {}: {}'.format(self.data['url'], e))
        if resp.status_code >= 400:
            raise ExecuteError('"{}" return code {}.'.format(self.data['url'], resp.status_code))
        data = resp.raw.read(1000, decode_content=True)
        if sys.version_info >= (3,):
            data = data.decode('utf-8', errors='ignore')
        return data


class ExecuteUrlServiceBase(ExecuteUrl):
    """Base class to create services execute classes
    """
    default_url = None  #: default url to call
    default_headers = None  #: default HTTP headers to send
    default_content_type = 'application/json'  #: default content type to send
    default_method = 'GET'  #: default HTTP method
    default_body = None  #: default body to send

    def __init__(self, name, data):
        """

        :param str name: name or mac address
        :param data: data on device section
        """
        super(ExecuteUrlServiceBase, self).__init__(name, data)
        self.data['url'] = self.get_url()
        self.data['headers'] = self.get_headers()
        self.data['content-type'] = self.get_content_type()
        self.data['method'] = self.get_method()
        self.data['body'] = self.get_body()

    def get_url(self):
        """Get url to call. By default default_url

        :return: url
        :rtype: str
        """
        return self.default_url

    def get_method(self):
        """Get HTTP method. By default default_method

        :return: HTTP method
        :rtype: str
        """
        return self.default_method

    def get_content_type(self):
        """Get HTTP content type to send. By default default_content_type

        :return: HTTP content type
        :rtype: str
        """
        return self.default_content_type

    def get_headers(self):
        """Get HTTP Headers to send. By default default_headers

        :return: HTTP Headers
        :rtype: dict
        """
        return copy.copy(self.default_headers or {})

    def get_body(self):
        """Get body to send. By default default_body

        :return: body content
        :rtype: str
        """
        return self.default_body


class ExecuteOwnApiBase(ExecuteUrlServiceBase):
    execute_name = None
    default_protocol = 'http'
    default_port = 0
    default_method = 'POST'

    def get_url(self):
        """API url

        :return: url
        :rtype: str
        """
        url = self.data[self.execute_name]
        parsed = urlparse(url)
        if not parsed.scheme:
            url = '{}://{}'.format(self.default_protocol, url)
        if not url.split(':')[-1].isalnum():
            url += ':{}'.format(self.default_port)
        return url

    def get_body(self):
        """Return "data" value on self.data

        :return: data to send
        :rtype: str
        """
        if self.default_body:
            return self.default_body
        data = self.data.get('data')
        if isinstance(data, dict):
            return json.dumps(data)
        return data


class ExecuteHomeAssistant(ExecuteOwnApiBase):
    """Send Home Assistant event

    https://home-assistant.io/developers/rest_api/#post-apieventsltevent_type
    """
    execute_name = 'homeassistant'
    default_port = 8123

    def get_url(self):
        """Home assistant url

        :return: url
        :rtype: str
        """
        url = super(ExecuteHomeAssistant, self).get_url()
        if not self.data.get('event'):
            raise InvalidConfig(extra_body='Event option is required for HomeAsistant on {} device.'.format(self.name))
        url += '/api/events/{}'.format(self.data['event'])
        return url

    def get_headers(self):
        headers = {}
        if 'access_token' in self.data:
            headers['Authorization'] = 'Bearer {0}'.format(self.data['access_token'])
        elif 'access' in self.data:
            headers['x-ha-access'] = self.data['access']

        return headers


class ExecuteOpenHab(ExecuteOwnApiBase):
    """Send Open Hab event

    """
    default_content_type = 'text/plain'
    execute_name = 'openhab'
    default_port = 8080

    def __init__(self, name, data):
        super(ExecuteOpenHab, self).__init__(name, data)
        self.data['headers'] = {'Accept': 'application/json'}

    def get_url(self):
        """Open Hab url

        :return: url
        :rtype: str
        """
        url = super(ExecuteOpenHab, self).get_url()
        if not self.data.get('item'):
            raise InvalidConfig(extra_body='Item option is required for Open Hab on {} device.'.format(self.name))
        url += '/rest/items/{}'.format(self.data['item'])
        return url

    def get_body(self):
        return self.data.get('state', 'ON')


class ExecuteIFTTT(ExecuteOwnApiBase):
    """Send IFTTT Webhook event.
    """
    execute_name = 'ifttt'
    url_pattern = 'https://maker.ifttt.com/trigger/{event}/with/key/{key}'

    def get_url(self):
        """IFTTT Webhook url

        :return: url
        :rtype: str
        """
        if not self.data[self.execute_name]:
            raise InvalidConfig(extra_body='Value for IFTTT is required on {} device. Get your key here: '
                                           'https://ifttt.com/services/maker_webhooks/settings'.format(self.name))
        if not self.data.get('event'):
            raise InvalidConfig(extra_body='Event option is required for IFTTT on {} device. '
                                           'You define the event name when creating a Webhook '
                                           'applet'.format(self.name))
        url = self.url_pattern.format(event=self.data['event'], key=self.data[self.execute_name])
        return url
