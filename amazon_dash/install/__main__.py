import os
import shutil

CONFIG_PATH = '/etc/amazon-dash.yml'

__dir__ = os.path.dirname(os.path.abspath(__file__))

CONFIG_EXAMPLE = os.path.join(__dir__, 'amazon-dash.yml')


class InstallException(Exception):
    pass


class IsInstallableException(InstallException):
    pass


class IsNecessaryException(InstallException):
    pass


class InstallBase(object):
    def is_installable(self):
        raise NotImplementedError

    def is_necessary(self):
        raise NotImplementedError

    def installation(self):
        raise NotImplementedError

    def install(self):
        self.is_installable()
        self.is_necessary()
        self.installation()


class InstallConfig(InstallBase):

    def is_installable(self):
        directory = os.path.dirname(CONFIG_PATH)
        if not os.path.lexists(directory):
            raise IsInstallableException('/{} does not exists'.format(directory))

    def is_necessary(self):
        if os.path.lexists(CONFIG_PATH):
            raise IsNecessaryException('{} already exists'.format(CONFIG_PATH))

    def installation(self):
        shutil.copy(CONFIG_EXAMPLE, CONFIG_PATH)
        os.chmod(CONFIG_PATH, 0o600)
        os.chown(CONFIG_PATH, 0, 0)
