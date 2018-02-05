import unittest

import os
from amazon_dash.tests._compat import patch

from amazon_dash.exceptions import InvalidConfig, InvalidDevice
from amazon_dash.listener import Listener, Device, last_execution, logger, test_device
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
        with patch.object(logger, 'warning') as warning_mock:
            device.execute()
            warning_mock.assert_called_once()

    def test_multiple_executes(self):
        data = {
            'cmd': 'ls',
            'url': 'http://domain.com',
        }
        with self.assertRaises(InvalidConfig):
            Device('key', data)

    def test_device_src(self):
        device = Device('key')
        device2 = Device(device)
        self.assertEqual(device.src, device2.src)


class TestTestListener(ExecuteMockBase, ConfigFileMockBase, unittest.TestCase):
    contents = config_data

    def test_invalid_device(self):
        with self.assertRaises(InvalidDevice):
            test_device('00:11:22:33:44:55', self.file)

    def test_success(self):
        test_device('44:65:0D:48:FA:88', self.file)
        self.execute_mock_req.assert_called_once()
