import unittest

import os

from amazon_dash.exceptions import SecurityException

from amazon_dash.listener import Listener, Device, last_execution
from amazon_dash.tests.base import ConfigFileMockBase, ExecuteMockBase

__dir__ = os.path.abspath(os.path.dirname(__file__))
config_data = open(os.path.join(__dir__, 'fixtures', 'config.yml')).read()


class TestListener(ExecuteMockBase, ConfigFileMockBase, unittest.TestCase):
    contents = config_data

    def test_create(self):
        listener = Listener(self.file)
        self.assertEqual(len(listener.devices), 2)

    def test_on_push(self):
        last_execution.clear()
        listener = Listener(self.file)
        listener.on_push(Device('0C:47:C9:98:4A:12'))
        self.execute_mock_req.assert_called_once()
        
    def test_double_called(self):
        last_execution.clear()
        listener = Listener(self.file)
        listener.on_push(Device('0C:47:C9:98:4A:12'))
        listener.on_push(Device('0C:47:C9:98:4A:12'))
        self.execute_mock_req.assert_called_once()


class TestDevice(ExecuteMockBase, unittest.TestCase):
    def test_create(self):
        data = {
            'cmd': "command",
            'user': "test",
            'cwd': "/dir",
            'name': "Command Name",
        }
        device = Device('KeY', data)
        self.assertEqual(device.src, 'key')
        self.assertEqual(device.name, data['name'])

    def test_name(self):
        device = Device('key')
        self.assertEqual(device.name, 'key')

    def test_no_execute(self):
        device = Device('key')
        device.execute()
