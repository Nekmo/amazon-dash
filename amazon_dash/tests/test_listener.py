import threading
import unittest

import os

from amazon_dash.confirmations import DisabledConfirmation
from amazon_dash.execute import ExecuteCmd
from amazon_dash.tests._compat import patch

from amazon_dash.exceptions import InvalidConfig, InvalidDevice
from amazon_dash.listener import Listener, Device, last_execution, logger, test_device
from amazon_dash.tests.base import ConfigFileMockBase, ExecuteMockBase

dirname = os.path.abspath(os.path.dirname(__file__))
config_data = open(os.path.join(dirname, 'fixtures', 'config.yml')).read()


class TestListener(ConfigFileMockBase, unittest.TestCase):
    contents = config_data

    def test_create(self):
        listener = Listener(self.file)
        self.assertEqual(len(listener.devices), 2)

    def test_on_push(self):
        last_execution.clear()
        listener = Listener(self.file)
        with patch('threading.Thread') as thread_mock:
            listener.on_push(Device('0C:47:C9:98:4A:12'))
            thread_mock.assert_called_once()
        
    def test_double_called(self):
        last_execution.clear()
        listener = Listener(self.file)
        with patch('threading.Thread') as thread_mock:
            listener.on_push(Device('0C:47:C9:98:4A:12'))
            listener.on_push(Device('0C:47:C9:98:4A:12'))
            thread_mock.assert_called_once()

    def test_thread_start(self):
        last_execution.clear()
        listener = Listener(self.file)
        with patch.object(threading.Thread, 'start') as thread_start_mock:
            listener.on_push(Device('0C:47:C9:98:4A:12'))
            thread_start_mock.assert_called_once()


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
        with patch.object(Device, 'send_confirmation') as send_confirmation_mock:
            device.execute()
            send_confirmation_mock.assert_called_once()

    def test_send_confirmation(self):
        device = Device('key', {'confirmation': 'tg'}, {'confirmations': {
            'tg': {'service': 'disabled'},
        }})
        with patch.object(DisabledConfirmation, 'send') as send_mock:
            device.execute()
            send_mock.assert_called_once()

    def test_execute_error(self):
        device = Device(
            'key', {
                'cmd': "command",
                'user': "test",
                'cwd': "/dir",
                'name': "Command Name",
            }, {'confirmations': {'tg': {'service': 'disabled'}}}
        )
        with patch.object(Device, 'send_confirmation') as send_confirmation_mock:
            self.execute_mock.stop()
            execute_mock = patch.object(ExecuteCmd, 'execute', side_effect=Exception())
            execute_mock.start()
            with self.assertRaises(Exception):
                device.execute()
            send_confirmation_mock.assert_called_once()
            execute_mock.stop()
            self.execute_mock.start()

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
