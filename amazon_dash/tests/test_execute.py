import json
import unittest

from amazon_dash.exceptions import SecurityException, InvalidConfig
from amazon_dash.execute import ExecuteCmd, ExecuteUrl
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

    def tearDown(self):
        super(TestExecuteUrl, self).tearDown()
        self.session_mock.stop()
