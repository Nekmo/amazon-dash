import json
import unittest
from threading import Thread

import requests
from requests_mock import NoMockAddress
from amazon_dash.tests._compat import patch as mock_patch, Mock

from amazon_dash.exceptions import SecurityException, InvalidConfig
from amazon_dash.execute import ExecuteCmd, ExecuteUrl, logger, execute_cmd, check_execution_success, get_shell, \
    ExecuteHomeAssistant
from amazon_dash.tests.base import ExecuteMockBase

import requests_mock

class TestExecuteCmd(ExecuteMockBase, unittest.TestCase):

    def test_execute(self):
        device = ExecuteCmd('key', {'cmd': 'ls'})
        device.execute()
        self.execute_mock_req.assert_called_once()

    def test_execute_root(self):
        device = ExecuteCmd('key', {'cmd': 'ls', 'user': 'root'})
        device.execute(True)
        self.execute_mock_req.assert_called_once()

    def test_execute_root_error(self):
        device = ExecuteCmd('key', {'cmd': 'ls', 'user': 'root'})
        with self.assertRaises(SecurityException):
            device.execute(False)
        self.execute_mock_req.assert_not_called()

    def test_execute_cmd_start(self):
        with mock_patch.object(Thread, 'start') as start_mock:
            execute_cmd('ls', '/tmp')
            start_mock.assert_called_once()

    @mock_patch('subprocess.Popen', autospec=True)
    def test_check_execution_success(self, popen_mock):
        popen_mock.return_value = Mock()
        popen_mock_obj = popen_mock.return_value

        popen_mock_obj.communicate.return_value = ("OUT", "ERR")
        popen_mock_obj.returncode = 1
        with mock_patch.object(logger, 'error') as logger_error:
            check_execution_success('ls', '/tmp')
            logger_error.assert_called_once()

    def test_get_shell(self):
        self.assertEqual(get_shell('/usr/bin/command'), ['/usr/bin/command'])
        self.assertEqual(get_shell('command'), ['/usr/bin/env', 'command'])


class TestExecuteUrl(unittest.TestCase):
    no_body_methods = ['get', 'head', 'delete', 'connect', 'options', 'trace']
    url = 'http://domain.com'
    
    def setUp(self):
        super(TestExecuteUrl, self).setUp()
        self.session_mock = requests_mock.Mocker()
        self.session_mock.start()
        self.get_mock = self.session_mock.get(self.url)
        pass

    def get_default_data(self):
        return {
            'url': self.url,
        }

    def test_content_type_invalid_method(self):
        data = dict(self.get_default_data(), **{
            'content-type': 'form',
        })
        for method in self.no_body_methods:
            with self.assertRaises(InvalidConfig):
                ExecuteUrl('key', dict(data, method=method)).validate()

    def test_body_invalid_method(self):
        data = dict(self.get_default_data(), **{
            'body': 'foo',
        })
        for method in self.no_body_methods:
            with self.assertRaises(InvalidConfig):
                ExecuteUrl('key', dict(data, method=method)).validate()

    def test_form_data(self):
        data = {'foo': 'bar'}
        execute_url = ExecuteUrl('key', dict(self.get_default_data(), method='post',
                                             body=json.dumps(data)))
        execute_url.validate()
        self.assertEqual(execute_url.data['body'], data)

    def test_form_invalid_data(self):
        execute_url = ExecuteUrl('key', dict(self.get_default_data(), method='post',
                                             body='{{inval'))
        with self.assertRaises(InvalidConfig):
            execute_url.validate()

    def test_execute(self):
        execute_url = ExecuteUrl('key', self.get_default_data())
        execute_url.validate()
        execute_url.execute()
        self.assertTrue(self.get_mock.called_once)

    def test_execute_headers(self):
        self.session_mock.post(self.url, request_headers={'authorization': 'foo'})
        execute_url = ExecuteUrl('key', dict(self.get_default_data(), method='post',
                                             **{'headers': {'authorization': 'foo'}}))
        execute_url.validate()
        execute_url.execute()
        execute_url2 = ExecuteUrl('key', dict(self.get_default_data(), method='post',
                                             **{'headers': {'authorization': 'bar'}}))
        execute_url2.validate()
        with self.assertRaises(NoMockAddress):
            execute_url2.execute()

    def test_execute_content_type(self):
        self.session_mock.post(self.url, request_headers={'content-type': 'foo'})
        execute_url = ExecuteUrl('key', dict(self.get_default_data(), method='post',
                                             **{'content-type': 'foo'}))
        execute_url.validate()
        execute_url.execute()
        execute_url2 = ExecuteUrl('key', dict(self.get_default_data(), method='post',
                                             **{'content-type': 'bar'}))
        execute_url2.validate()
        with self.assertRaises(NoMockAddress):
            execute_url2.execute()

    def test_execute_body(self):
        self.session_mock.post(self.url, additional_matcher=lambda r: r.body == 'foo')
        execute_url = ExecuteUrl('key', dict(self.get_default_data(), method='post', body='foo',
                                             **{'content-type': 'plain'}))
        execute_url.validate()
        execute_url.execute()
        execute_url2 = ExecuteUrl('key', dict(self.get_default_data(), method='post', body='bar',
                                             **{'content-type': 'plain'}))
        execute_url2.validate()
        with self.assertRaises(NoMockAddress):
            execute_url2.execute()

    def test_execute_exception(self):
        self.session_mock.post(self.url, exc=requests.exceptions.ConnectTimeout)
        execute_url = ExecuteUrl('key', dict(self.get_default_data(), method='post', body='foo',
                                             **{'content-type': 'plain'}))
        execute_url.validate()
        with mock_patch.object(logger, 'warning') as warning_mock:
            execute_url.execute()
            warning_mock.assert_called_once()

    def test_execute_400(self):
        self.session_mock.post(self.url, status_code=400)
        execute_url = ExecuteUrl('key', dict(self.get_default_data(), method='post',
                                             **{'content-type': 'plain'}))
        execute_url.validate()
        with mock_patch.object(logger, 'warning') as warning_mock:
            execute_url.execute()
            warning_mock.assert_called_once()

    def tearDown(self):
        super(TestExecuteUrl, self).tearDown()
        self.session_mock.stop()


class TestExecuteHomeAssistant(unittest.TestCase):
    path = '/api/events/test'
    url = 'http://localhost:8123' + path

    def default_data(self, address='localhost', event='test'):
        return {
            'homeassistant': address,
            'event': event,
        }

    def test_no_event(self):
        with self.assertRaises(InvalidConfig):
            ExecuteHomeAssistant('key', self.default_data(event=''))

    def test_only_address(self):
        assis = ExecuteHomeAssistant('key', self.default_data())
        self.assertIn('url', assis.data)
        self.assertEqual(assis.data['url'], self.url)

    def test_include_address_protocol(self):
        assis = ExecuteHomeAssistant('key', self.default_data('https://localhost'))
        self.assertIn('url', assis.data)
        self.assertEqual(assis.data['url'], 'https://localhost:8123' + self.path)

    def test_include_address_port(self):
        assis = ExecuteHomeAssistant('key', self.default_data('localhost:7123'))
        self.assertIn('url', assis.data)
        self.assertEqual(assis.data['url'], 'http://localhost:7123' + self.path)

    def test_full_address(self):
        assis = ExecuteHomeAssistant('key', self.default_data('https://localhost:7123'))
        self.assertIn('url', assis.data)
        self.assertEqual(assis.data['url'], 'https://localhost:7123' + self.path)

    def test_execute(self):
        with requests_mock.mock() as m:
            m.post(self.url, text='success')
            assis = ExecuteHomeAssistant('key', self.default_data())
            assis.execute()
            self.assertTrue(m.called_once)
