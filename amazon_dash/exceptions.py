import os


class SecurityException(Exception):
    pass


class ConfigFileNotFoundError(FileNotFoundError):
    def __init__(self, file):
        file = file if os.path.isabs(file) else os.path.join(os.getcwd(), file)
        super(ConfigFileNotFoundError, self).__init__('The configuration file was not found on "{}"'.format(file))
