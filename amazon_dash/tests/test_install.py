import unittest
import os

from click.testing import CliRunner

from ._compat import patch

from pyfakefs.fake_filesystem_unittest import Patcher

from amazon_dash.install import InstallConfig, IsInstallableException, CONFIG_PATH, IsNecessaryException, \
    CONFIG_EXAMPLE, SYSTEMD_PATHS, InstallSystemd, SYSTEMD_SERVICE, cli


class TestInstallConfig(unittest.TestCase):
    def test_is_installable(self):
        with Patcher() as patcher:
            with self.assertRaises(IsInstallableException):
                InstallConfig().is_installable()
            patcher.fs.CreateFile(CONFIG_PATH)
            InstallConfig().is_installable()

    def test_is_necessary(self):
        with Patcher() as patcher:
            InstallConfig().is_necessary()
            patcher.fs.CreateFile(CONFIG_PATH)
            with self.assertRaises(IsNecessaryException):
                InstallConfig().is_necessary()

    def test_installation(self):
        with Patcher() as patcher:
            os.makedirs(os.path.dirname(CONFIG_PATH))
            patcher.fs.CreateFile(CONFIG_EXAMPLE)
            InstallConfig().installation()
            stat = os.stat(CONFIG_PATH)
            self.assertEqual(stat.st_mode, 0o100600)
            self.assertEqual(stat.st_uid, 0)
            self.assertEqual(stat.st_gid, 0)


class TestInstallSystemd(unittest.TestCase):
    @patch('amazon_dash.install.get_init_system', return_value='systemd')
    def test_is_installable(self, mock_check_output):
        with Patcher() as patcher:
            with self.assertRaises(IsInstallableException):
                InstallSystemd().is_installable()
            patcher.fs.CreateFile(SYSTEMD_PATHS[0])
            InstallSystemd().is_installable()

    def test_is_necessary(self):
        with Patcher() as patcher:
            os.makedirs(SYSTEMD_PATHS[0])
            InstallSystemd().is_necessary()
            path = os.path.join(SYSTEMD_PATHS[0], os.path.split(SYSTEMD_SERVICE)[1])
            patcher.fs.CreateFile(path)
            with self.assertRaises(IsNecessaryException):
                InstallSystemd().is_necessary()

    def test_installation(self):
        with Patcher() as patcher:
            os.makedirs(SYSTEMD_PATHS[0])
            path = os.path.join(SYSTEMD_PATHS[0], os.path.split(SYSTEMD_SERVICE)[1])
            patcher.fs.CreateFile(SYSTEMD_SERVICE)
            InstallSystemd().installation()
            stat = os.stat(path)
            self.assertEqual(stat.st_mode, 0o100600)
            self.assertEqual(stat.st_uid, 0)
            self.assertEqual(stat.st_gid, 0)


class TestClickAll(unittest.TestCase):
    @patch('amazon_dash.install.get_init_system', return_value='systemd')
    def test_no_services(self, mock_check_output):
        with Patcher() as patcher:
            patcher.fs.CreateFile(CONFIG_PATH)
            runner = CliRunner()
            result = runner.invoke(cli, ['--root-not-required', 'all'])
            self.assertIn('You must run Amazon-dash manually', result.output)

    @patch('amazon_dash.install.get_init_system', return_value='systemd')
    def test_is_not_necessary(self, mock_check_output):
        with Patcher() as patcher:
            patcher.fs.CreateFile(CONFIG_PATH)
            path = os.path.join(SYSTEMD_PATHS[0], os.path.split(SYSTEMD_SERVICE)[1])
            patcher.fs.CreateFile(path)
            runner = CliRunner()
            result = runner.invoke(cli, ['--root-not-required', 'all'])
            self.assertIn('Systemd service is already installed', result.output)
