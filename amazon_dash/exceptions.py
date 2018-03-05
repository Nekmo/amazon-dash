import os

import click

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class AmazonDashException(Exception):
    """Amazon Dash base exception. All the exceptions that use this base are captured by the command line.
    """
    error_code = 3  #: Error code to return


class SecurityException(AmazonDashException):
    """A configuration fault has been found that puts the system at risk
    """
    error_code = 4  #: Error code to return


class ConfigFileNotFoundError(AmazonDashException, FileNotFoundError):
    """The configuration file was not found
    """
    error_code = 5  #: Error code to return

    def __init__(self, file):
        """
        :param str file: Path to config path used
        """
        file = os.path.abspath(file)
        super(ConfigFileNotFoundError, self).__init__('The configuration file was not found on "{}"'.format(file))


class InvalidConfig(AmazonDashException):
    """The configuration file has not passed the yaml validation or json-schema validation or exec. class validation
    """
    error_code = 6  #: Error code to return

    def __init__(self, file=None, extra_body=''):
        """
        :param str file: Path to config file
        :param extra_body: complementary message
        """
        body = 'The configuration file is invalid'
        if file:
            file = os.path.abspath(file)
            body += ' ({})'.format(file)
        body += '. Check the file and read the documentation.'.format(file)
        if extra_body:
            body += ' {}'.format(extra_body)
        super(InvalidConfig, self).__init__(body)


class SocketPermissionError(AmazonDashException):
    """The program must be run as root or the user needs permissions to sniff the traffic
    """
    error_code = 7  #: Error code to return

    def __init__(self):
        msg = 'This program needs permission to open raw sockets on your system. ' \
              'The easy way to run this program is to use root. To use a normal user,' \
              ' consult the documentation.'
        super(SocketPermissionError, self).__init__(msg)


class InvalidDevice(AmazonDashException):
    """Used on test-device command. The mac address device is not in config file
    """
    error_code = 8  #: Error code to return


class ConfirmationError(AmazonDashException):
    """A An error occurred while sending the confirmation
    """
    error_code = 9  #: Error code to return


class ExecuteError(AmazonDashException):
    """A An error occurred while executing a device
    """
    error_code = 10  #: Error code to return


def catch(fn, exception_cls=None, raises=True):
    exception_cls = exception_cls or AmazonDashException

    def wrap(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except exception_cls as e:
            click.secho('[Error] Amazon Dash Exception ({}):\n{}\n'.format(
                e.__class__.__name__ if isinstance(e, exception_cls) else e, e),
                err=True, fg='red',
            )
            if raises:
                exit(getattr(e, 'error_code', 99))
    return wrap
