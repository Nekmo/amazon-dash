import os
import shutil
import sys
from subprocess import check_output

import click as click
from click_default_group import DefaultGroup
from amazon_dash.install.exceptions import InstallException, IsInstallableException, IsNecessaryException

CONFIG_PATH = '/etc/amazon-dash.yml'
SYSTEMD_PATHS = [
    '/usr/lib/systemd/system',
    '/lib/systemd/system',
]
dirname = os.path.dirname(os.path.abspath(__file__))
CONFIG_EXAMPLE = os.path.join(dirname, 'amazon-dash.yml')
SYSTEMD_SERVICE = os.path.join(dirname, 'services', 'amazon-dash.service')


if sys.version_info < (3,0):
    FileNotFoundError = OSError


def get_pid(name):
    return check_output(["pidof", name])


def get_init_system():
    try:
        return check_output(['ps', '--no-headers', '-o', 'comm', '1']).strip(b'\n ').decode('utf-8')
    except FileNotFoundError:
        raise IsInstallableException('"ps" command is unavailable on your OS. systemd.'
                                     'The systemd check could not be finalized.')


def get_systemd_services_path():
    for path in SYSTEMD_PATHS:
        if os.path.lexists(path):
            return path


def catch(fn, exception_cls=None):
    exception_cls = exception_cls or InstallException

    def wrap(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except exception_cls as e:
            click.echo('{}'.format(e), err=True)
    return wrap


def install_success(name):
    click.echo('[OK] {} has been installed successfully'.format(name))
    return True


class InstallBase(object):
    name = ''

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
        return True


class InstallConfig(InstallBase):
    name = 'config'

    def is_installable(self):
        directory = os.path.dirname(CONFIG_PATH)
        if not os.path.lexists(directory):
            raise IsInstallableException('{} does not exists'.format(directory))

    def is_necessary(self):
        if os.path.lexists(CONFIG_PATH):
            raise IsNecessaryException('{} already exists'.format(CONFIG_PATH))

    def installation(self):
        shutil.copy(CONFIG_EXAMPLE, CONFIG_PATH)
        os.chmod(CONFIG_PATH, 0o600)
        os.chown(CONFIG_PATH, 0, 0)


class InstallSystemd(InstallBase):
    name = 'systemd'
    service_name = os.path.split(SYSTEMD_SERVICE)[-1]

    @property
    def service_path(self):
        path = get_systemd_services_path()
        if not path:
            return
        return os.path.join(path, self.service_name)

    def is_installable(self):
        if get_init_system() != 'systemd' or not get_systemd_services_path():
            raise IsInstallableException('Systemd is not available')

    def is_necessary(self):
        if os.path.lexists(self.service_path):
            raise IsNecessaryException('Systemd service is already installed')

    def installation(self):
        shutil.copy(SYSTEMD_SERVICE, self.service_path)
        os.chmod(self.service_path, 0o600)
        os.chown(self.service_path, 0, 0)


SERVICES = [
    InstallSystemd,
]


@click.group(cls=DefaultGroup, default='all', default_if_no_args=True)
@click.option('--root-required/--root-not-required', default=True)
def cli(root_required):
    if os.getuid() and root_required:
        click.echo('The installation must be done as root. Maybe you forgot sudo?', err=True)
        sys.exit(1)


@catch
@cli.command()
def config():
    InstallConfig().install() and install_success('config')


@catch
@cli.command()
def systemd():
    InstallSystemd().install() and install_success('systemd service')


@cli.command()
def all():
    click.echo('Executing all install scripts for Amazon-Dash')
    catch(InstallConfig().install)() and install_success('config')
    has_service = False
    for service in SERVICES:
        try:
            has_service = has_service or (service().install() and
                                          install_success('{} service'.format(service.name)))
        except IsInstallableException:
            pass
        except IsNecessaryException as e:
            has_service = True
            click.echo('{}'.format(e), err=True)
    if not has_service:
        click.echo('Warning: There is no service installed in the system. You must run Amazon-dash manually')
