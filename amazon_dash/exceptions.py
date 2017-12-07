

class SecurityException(Exception):
    pass


class ConfigFileNotFoundError(FileNotFoundError):
    def __init__(self, file):
        super(ConfigFileNotFoundError, self).__init__('The configuration file was not found on "{}"'.format(file))