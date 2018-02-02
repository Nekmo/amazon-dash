import os
import shutil

from subprocess import check_output

CONFIG_PATH = '/etc/amazon-dash.yml'
SYSTEMD_PATHS = [
    '/usr/lib/systemd/system',
    '/lib/systemd/system',
]

__dir__ = os.path.dirname(os.path.abspath(__file__))

CONFIG_EXAMPLE = os.path.join(__dir__, 'amazon-dash.yml')
SYSTEMD_SERVICE = os.path.join(__dir__, 'services', 'amazon-dash.service')


def get_pid(name):
    return check_output(["pidof", name])


def get_systemd_services_path():
    for path in SYSTEMD_PATHS:
        if os.path.lexists(path):
            return path


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


class InstallSystemd(InstallBase):
    service_name = os.path.split(SYSTEMD_SERVICE)[-1]

    @property
    def service_path(self):
        path = get_systemd_services_path()
        if not path:
            return
        return os.path.join(path, self.service_name)

    def is_installable(self):
        if not get_pid('systemd') and get_systemd_services_path():
            raise IsInstallableException('Systemd is not available')

    def is_necessary(self):
        if os.path.lexists(self.service_path):
            raise IsInstallableException('Systemd is not available')

    def installation(self):
        shutil.copy(SYSTEMD_SERVICE, self.service_path)
        os.chmod(self.service_path, 0o600)
        os.chown(self.service_path, 0, 0)
