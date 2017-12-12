import os


class AmazonDashException(Exception):
    pass


class SecurityException(AmazonDashException):
    pass


class ConfigFileNotFoundError(AmazonDashException, FileNotFoundError):
    def __init__(self, file):
        file = os.path.abspath(file)
        super(ConfigFileNotFoundError, self).__init__('The configuration file was not found on "{}"'.format(file))


class InvalidConfig(AmazonDashException):
    def __init__(self, file=None, extra_body=''):
        body = 'The configuration file is invalid'
        if file:
            file = os.path.abspath(file)
            body += '({})'.format(file)
        body += '. Check the file and read the documentation.'.format(file)
        if extra_body:
            body += ' {}'.format(extra_body)
        super(InvalidConfig, self).__init__(body)


class SocketPermissionError(AmazonDashException):
    def __init__(self):
        msg = 'This program needs permission to open raw sockets on your system. ' \
              'The easy way to run this program is to use root. To use a normal user,' \
              ' consult the documentation.'
        super(SocketPermissionError, self).__init__(msg)