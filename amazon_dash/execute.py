import json
import logging
import subprocess
import threading

import getpass

from requests import request, RequestException
from amazon_dash._compat import JSONDecodeError
from amazon_dash.exceptions import SecurityException, InvalidConfig
from ._compat import urlparse

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
    return ['sudo', '-s', '--set-home', '-u', user] + get_shell(shell) + [EXECUTE_SHELL_PARAM, cmd]


def check_execution_success(cmd, cwd):
    """Execute a command and show error on fail

    :param str cmd: command
    :param str cwd: current working directory
    :return: None
    """
    p = subprocess.Popen(cmd, cwd=cwd, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode:
        logger.error('%i return code on "%s" command. Stderr: %s', p.returncode, ' '.join(cmd), stderr)


def execute_cmd(cmd, cwd=None):
    """Excecute command on thread

    :param cmd: Command to execute
    :param cwd: current working directory
    :return: None
    """
    l = threading.Thread(target=check_execution_success, args=(cmd, cwd))
    l.daemon = True
    l.start()


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
        if self.user == ROOT_USER and not root_allowed:
            raise SecurityException('For security, execute commands as root is not allowed. '
                                    'Use --root-allowed to allow executing commands as root. '
                                    ' It is however recommended to add a user to the configuration '
                                    'of the device (device: {})'.format(self.name))
        cmd = run_as_cmd(self.data['cmd'], self.user)
        execute_cmd(cmd, self.data.get('cwd'))


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
        kwargs = {'headers': self.data.get('headers', {})}
        if self.data.get('content-type'):
            kwargs['headers']['content-type'] = self.data['content-type']
        if self.data.get('body'):
            kwargs['data'] = self.data['body']
        try:
            resp = request(self.data.get('method', 'get').lower(), self.data['url'], **kwargs)
        except RequestException as e:
            logger.warning('Exception on request to {}: {}'.format(self.data['url'], e))
            return
        if resp.status_code >= 400:
            logger.warning('"{}" return code {}.'.format(self.data['url'], resp.status_code))


class ExecuteUrlServiceBase(ExecuteUrl):
    """Base class to create services execute classes
    """
    default_url = None  #: default url to call
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
        self.data['content_type'] = self.get_content_type()
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

    def get_body(self):
        """Get body to send. By default default_body

        :return: body content
        :rtype: str
        """
        return self.default_body


class ExecuteHomeAssistant(ExecuteUrlServiceBase):
    """Send Home Assistant event

    https://home-assistant.io/developers/rest_api/#post-apieventsltevent_type
    """
    default_method = 'POST'

    def get_url(self):
        """Home assistant url

        :return: url
        :rtype: str
        """
        url = self.data['homeassistant']
        parsed = urlparse(url)
        if not parsed.scheme:
            url = 'http://{}'.format(url)
        if not url.split(':')[-1].isalnum():
            url += ':8123'
        if not self.data.get('event'):
            raise InvalidConfig(extra_body='Event option is required for HomeAsistant on {} device.'.format(self.name))
        url += '/api/events/{}'.format(self.data['event'])
        return url

    def get_body(self):
        """Return "data" value on self.data

        :return: data to send
        :rtype: str
        """
        return self.data.get('data')
