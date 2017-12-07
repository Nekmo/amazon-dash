import os


class SecurityException(Exception):
    pass


class ConfigFileNotFoundError(FileNotFoundError):
    def __init__(self, file):
        file = os.path.abspath(file)
        super(ConfigFileNotFoundError, self).__init__('The configuration file was not found on "{}"'.format(file))


class InvalidConfig(Exception):
    def __init__(self, file, extra_body=''):
        file = os.path.abspath(file)
        body = 'The configuration file is invalid ({}). Check the file and read the documentation.'.format(file)
        if extra_body:
            body += ' {}'.format(extra_body)
        super(InvalidConfig, self).__init__(body)
