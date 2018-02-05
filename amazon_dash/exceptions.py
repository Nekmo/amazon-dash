import os

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class AmazonDashException(Exception):
    """Amazon Dash base exception. All the exceptions that use this base are captured by the command line.
    """
    pass


class SecurityException(AmazonDashException):
    """A configuration fault has been found that puts the system at risk
    """
    pass


class ConfigFileNotFoundError(AmazonDashException, FileNotFoundError):
    """The configuration file was not found
    """
    def __init__(self, file):
        """
        :param str file: Path to config path used
        """
        file = os.path.abspath(file)
        super(ConfigFileNotFoundError, self).__init__('The configuration file was not found on "{}"'.format(file))


class InvalidConfig(AmazonDashException):
    """The configuration file has not passed the yaml validation or json-schema validation or exec. class validation
    """
    def __init__(self, file=None, extra_body=''):
        """
        :param str file: Path to config file
        :param extra_body: complementary message
        """
        body = 'The configuration file is invalid'
        if file:
            file = os.path.abspath(file)
            body += '({})'.format(file)
        body += '. Check the file and read the documentation.'.format(file)
        if extra_body:
            body += ' {}'.format(extra_body)
        super(InvalidConfig, self).__init__(body)


class SocketPermissionError(AmazonDashException):
    """The program must be run as root or the user needs permissions to sniff the traffic
    """
    def __init__(self):
        msg = 'This program needs permission to open raw sockets on your system. ' \
              'The easy way to run this program is to use root. To use a normal user,' \
              ' consult the documentation.'
        super(SocketPermissionError, self).__init__(msg)


class InvalidDevice(AmazonDashException):
    """Used on test-device command. The mac address device is not in config file
    """
    pass
