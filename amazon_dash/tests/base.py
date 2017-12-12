import os
from ._compat import patch
from pyfakefs.fake_filesystem_unittest import Patcher


class FileMockBase(object):
    contents = ''

    def setUp(self):
        self.patcher = Patcher()
        self.patcher.setUp()
        self.file = 'config.yml'
        self.patcher.fs.CreateFile(self.file, contents=self.contents)

    def tearDown(self):
        self.patcher.tearDown()


class ConfigFileMockBase(FileMockBase):
    def setUp(self):
        self.getuid_mock = patch('os.getuid', return_value=1000)
        self.getuid_mock.start()
        super(ConfigFileMockBase, self).setUp()
        os.chown(self.file, 1000, 1000)
        os.chmod(self.file, 0o660)

    def tearDown(self):
        self.getuid_mock.stop()
        super(ConfigFileMockBase, self).tearDown()


class ExecuteMockBase(object):
    def setUp(self):
        self.execute_mock = patch('amazon_dash.execute.execute_cmd', return_value=None)
        self.execute_mock_req = self.execute_mock.start()
        super(ExecuteMockBase, self).setUp()

    def tearDown(self):
        self.execute_mock.stop()
        super(ExecuteMockBase, self).tearDown()

