import os
import unittest
from ._compat import patch

from pyfakefs.fake_filesystem_unittest import Patcher

from amazon_dash.config import Config, only_root_write, oth_w_perm, check_config
from amazon_dash.exceptions import SecurityException, InvalidConfig
from amazon_dash.tests.base import FileMockBase

dirname = os.path.abspath(os.path.dirname(__file__))
config_data = open(os.path.join(dirname, 'fixtures', 'config.yml')).read()


try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class TestConfig(unittest.TestCase):

    @patch('os.path.lexists', return_value=False)
    def test_not_found(self, mock_method):
        with self.assertRaises(FileNotFoundError):
            Config('config.yml')
        mock_method.assert_called_once()

    def test_yaml_exception(self):
        file = 'config.yml'
        with Patcher() as patcher:
            patcher.fs.CreateFile(file, contents='\x00')
            os.chown(file, 0, 0)
            os.chmod(file, 0o660)
            with self.assertRaises(InvalidConfig):
                Config('config.yml')

    @patch('os.getuid', return_value=1000)
    def test_other_user(self, getuid_mock):
        file = 'amazon-dash.yml'
        with Patcher() as patcher:
            patcher.fs.CreateFile(file, contents=config_data)
            os.chown(file, 1000, 1000)
            os.chmod(file, 0o660)
            Config(file)
        patcher.tearDown()

    @patch('amazon_dash.config.get_file_group', return_value='test')
    @patch('amazon_dash.config.get_file_owner', return_value='test')
    @patch('os.getuid', return_value=1000)
    def test_other_user_error(self, getuid_mock, file_owner_mock, file_group_mock):
        file = 'amazon-dash.yml'
        with Patcher() as patcher:
            patcher.fs.CreateFile(file, contents=config_data)
            os.chown(file, 1000, 1000)
            os.chmod(file, 0o666)
            with self.assertRaises(SecurityException):
                Config(file)
        patcher.tearDown()

    @patch('os.getuid', return_value=0)
    def test_root(self, getuid_mock):
        file = 'amazon-dash.yml'
        with Patcher() as patcher:
            patcher.fs.CreateFile(file, contents=config_data)
            os.chown(file, 0, 0)
            os.chmod(file, 0o660)
            Config(file)
        patcher.tearDown()

    @patch('amazon_dash.config.get_file_group', return_value='root')
    @patch('amazon_dash.config.get_file_owner', return_value='root')
    @patch('os.getuid', return_value=0)
    def test_root_error(self, getuid_mock, file_owner_mock, file_group_mock):
        file = 'amazon-dash.yml'
        with Patcher() as patcher:
            patcher.fs.CreateFile(file, contents=config_data)
            os.chown(file, 1000, 1000)
            os.chmod(file, 0o660)
            with self.assertRaises(SecurityException):
                Config(file)
        patcher.tearDown()

    @patch('os.getuid', return_value=1000)
    def test_invalid_config(self, getuid_mock):
        file = 'amazon-dash.yml'
        with Patcher() as patcher:
            patcher.fs.CreateFile(file, contents='invalid config')
            os.chown(file, 1000, 1000)
            os.chmod(file, 0o660)
            with self.assertRaises(InvalidConfig):
                Config(file)


class TestOthWPerm(FileMockBase, unittest.TestCase):
    def test_perms(self):
        os.chmod(self.file, 0o666)
        self.assertTrue(oth_w_perm(self.file))

    def test_no_perms(self):
        os.chmod(self.file, 0o660)
        self.assertFalse(oth_w_perm(self.file))


class TestOnlyRootWrite(FileMockBase, unittest.TestCase):

    def test_root_owner(self):
        os.chown(self.file, 0, 0)
        os.chmod(self.file, 0o660)
        self.assertTrue(only_root_write(self.file))

    def test_no_perms(self):
        os.chown(self.file, 1000, 1000)
        os.chmod(self.file, 0o000)
        self.assertTrue(only_root_write(self.file))

    def test_other_perms(self):
        os.chown(self.file, 0, 0)
        os.chmod(self.file, 0o666)
        self.assertFalse(only_root_write(self.file))

    def test_user_owner(self):
        os.chown(self.file, 1000, 1000)
        os.chmod(self.file, 0o660)
        self.assertFalse(only_root_write(self.file))


class TestCheckConfig(unittest.TestCase):
    def test_fail(self):
        file = 'amazon-dash.yml'
        with Patcher() as patcher:
            patcher.fs.CreateFile(file, contents='invalid config')
            os.chown(file, 0, 0)
            os.chmod(file, 0o600)
            with self.assertRaises(InvalidConfig):
                check_config(file)

    def test_success(self):
        file = 'amazon-dash.yml'
        with Patcher() as patcher:
            patcher.fs.CreateFile(file, contents=config_data)
            os.chown(file, 0, 0)
            os.chmod(file, 0o600)
            check_config(file, lambda x: x)
