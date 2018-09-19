import base64
import json
import unittest
from threading import Thread

import requests
import sys
from requests_mock import NoMockAddress
from amazon_dash._compat import subprocess
from amazon_dash.tests._compat import patch as mock_patch, Mock

from amazon_dash.exceptions import SecurityException, InvalidConfig, ExecuteError
from amazon_dash.execute import ExecuteCmd, ExecuteUrl, logger, execute_cmd, get_shell, \
    ExecuteHomeAssistant, ExecuteOpenHab, ExecuteIFTTT, execute_over_ssh
from amazon_dash.tests.base import ExecuteMockBase

import requests_mock


def io_out(text):
    if sys.version_info >= (3, 0):
        from io import BytesIO
        return BytesIO(bytes(text, 'utf-8'))
    else:
        from StringIO import StringIO
        return StringIO('foo')


class TestExecuteCmdFunction(unittest.TestCase):

    @mock_patch.object(subprocess, 'Popen')
    def test_success(self, m):
        process_mock = Mock()
        process_mock.configure_mock(**{'returncode': 0, 'stdout': io_out('foo')})
        m.return_value = process_mock
        out = execute_cmd(['ls'])
        self.assertEqual(out[0], 'foo')

    @mock_patch.object(subprocess, 'Popen')
    def test_error(self, m):
        process_mock = Mock()
        process_mock.configure_mock(**{'returncode': 1})
        m.return_value = process_mock
        with self.assertRaises(ExecuteError):
            execute_cmd(['ls'])

    @mock_patch.object(subprocess, 'Popen')
    def test_timeout(self, m):
        def side_effect(timeout=None):
            raise subprocess.TimeoutExpired('', timeout)

        process_mock = Mock()
        process_mock.configure_mock(**{'wait.side_effect': side_effect})
        m.return_value = process_mock
        self.assertEqual(execute_cmd(['ls']), None)


class TestExecuteOverSsh(unittest.TestCase):
    def test_invalid_port(self):
        with self.assertRaises(InvalidConfig):
            execute_over_ssh('ls', 'machine:spam')

    def test_execute_without_port(self):
        cmd = execute_over_ssh('ls', 'machine')
        self.assertEqual(['ssh', 'machine', '-C', "/usr/bin/env bash -c ' ls '"], cmd)

    def test_execute_with_port(self):
        cmd = execute_over_ssh('ls', 'machine:222')
        self.assertEqual(['ssh', 'machine', '-p', '222', '-C', "/usr/bin/env bash -c ' ls '"], cmd)

    def test_execute_double_quotes(self):
        cmd = execute_over_ssh('"ls"', 'machine:222')
        self.assertEqual(['ssh', 'machine', '-p', '222', '-C', "/usr/bin/env bash -c ' \"ls\" '"], cmd)

    def test_execute_single_quotes(self):
        cmd = execute_over_ssh('\'ls\'', 'machine:222')
        self.assertEqual(['ssh', 'machine', '-p', '222', '-C', "/usr/bin/env bash -c ' '\"'\"'ls'\"'\"' '"], cmd)


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

    def test_user_on_ssh(self):
        device = ExecuteCmd('key', {'cmd': 'ls', 'user': 'root', 'ssh': 'machine'})
        with self.assertRaises(InvalidConfig):
            device.execute()
        self.execute_mock_req.assert_not_called()

    def test_ssh(self):
        device = ExecuteCmd('key', {'cmd': 'ls', 'ssh': 'machine'})
        with mock_patch('amazon_dash.execute.execute_over_ssh') as execute_over_ssh_mock:
            device.execute()
            execute_over_ssh_mock.assert_called_once()
        self.execute_mock_req.assert_called_once()

    # def test_execute_cmd_start(self):
    #     with mock_patch.object(Thread, 'start') as start_mock:
    #         execute_cmd('ls', '/tmp')
    #         start_mock.assert_called_once()

    # @mock_patch('subprocess.Popen', autospec=True)
    # def test_check_execution_success(self, popen_mock):
    #     popen_mock.return_value = Mock()
    #     popen_mock_obj = popen_mock.return_value
    #
    #     popen_mock_obj.communicate.return_value = ("OUT", "ERR")
    #     popen_mock_obj.returncode = 1
    #     with mock_patch.object(logger, 'error') as logger_error:
    #         check_execution_success('ls', '/tmp')
    #         logger_error.assert_called_once()

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
        with self.assertRaises(ExecuteError):
            execute_url.execute()

    def test_execute_400(self):
        self.session_mock.post(self.url, status_code=400)
        execute_url = ExecuteUrl('key', dict(self.get_default_data(), method='post',
                                             **{'content-type': 'plain'}))
        execute_url.validate()
        with self.assertRaises(ExecuteError):
            execute_url.execute()

    def test_authorization(self):
        auth = b'Basic ' + base64.b64encode(b'foo:bar')
        auth = auth.decode('utf-8') if sys.version_info > (3,) else auth
        self.session_mock.post(self.url, request_headers={'Authorization': auth})
        execute_url = ExecuteUrl('key', dict(self.get_default_data(), method='post', auth='foo:bar'))
        execute_url.validate()
        execute_url.execute()

    def test_verify(self):
        ExecuteUrl('key', dict(self.get_default_data(), verify=False)).execute()
        self.assertFalse(self.session_mock.last_request.verify)

    def tearDown(self):
        super(TestExecuteUrl, self).tearDown()
        self.session_mock.stop()


class TestExecuteHomeAssistant(unittest.TestCase):
    path = '/api/events/test'
    url = 'http://localhost:8123' + path

    def default_data(self, address='localhost', event='test', extra_data=None):
        return dict({
            'homeassistant': address,
            'event': event,
        }, **extra_data or {})

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

    def test_execute_with_access(self):
        with requests_mock.mock() as m:
            m.post(self.url, text='success', request_headers={'x-ha-access': 'password'})
            assis = ExecuteHomeAssistant('key', self.default_data(extra_data={'access': 'password'}))
            assis.execute()
            self.assertTrue(m.called_once)

    def test_execute_with_access_token(self):
        with requests_mock.mock() as m:
            m.post(self.url, text='success', request_headers={'Authorization': 'Bearer abcde12345'})
            assis = ExecuteHomeAssistant('key', self.default_data(extra_data={'access_token': 'abcde12345'}))
            assis.execute()
            self.assertTrue(m.called_once)


class TestExecuteOpenHab(unittest.TestCase):
    path = '/rest/items/test'
    url = 'http://localhost:8080' + path

    def default_data(self, address='localhost', item='test'):
        return {
            'openhab': address,
            'item': item,
        }

    def test_execute(self):
        with requests_mock.mock() as m:
            m.post(self.url, text='success',
                   request_headers={'Content-Type': 'text/plain', 'Accept': 'application/json'})
            assis = ExecuteOpenHab('key', self.default_data())
            assis.execute()
            self.assertTrue(m.called_once)


class TestExecuteIFTTT(unittest.TestCase):

    def default_data(self):
        return {
            'ifttt': 'foobarspam' * 5,
            'event': 'myevent',
        }

    def test_execute(self):
        data = self.default_data()
        with requests_mock.mock() as m:
            m.post(ExecuteIFTTT.url_pattern.format(key=data['ifttt'], **data))
            assis = ExecuteIFTTT('key', data)
            assis.execute()
            self.assertTrue(m.called_once)

    def test_key_required(self):
        data = self.default_data()
        data['ifttt'] = ''
        with self.assertRaises(InvalidConfig):
            ExecuteIFTTT('key', data)

    def test_event_required(self):
        data = self.default_data()
        data['event'] = ''
        with self.assertRaises(InvalidConfig):
            ExecuteIFTTT('key', data)
