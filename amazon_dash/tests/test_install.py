import unittest

from pyfakefs.fake_filesystem_unittest import Patcher

from amazon_dash.install import InstallConfig, IsInstallableException


class TestInstallConfig(unittest.TestCase):
    def test_is_installable(self):
        with Patcher() as patcher:
            with self.assertRaises(IsInstallableException):
                InstallConfig().is_installable()
            # patcher.fs.create_file('/foo/bar', contents='test')
