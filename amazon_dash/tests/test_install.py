import unittest

import os
from pyfakefs.fake_filesystem_unittest import Patcher

from amazon_dash.install import InstallConfig, IsInstallableException, CONFIG_PATH, IsNecessaryException, CONFIG_EXAMPLE


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
