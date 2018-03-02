import unittest

import requests
import requests_mock

from amazon_dash.confirmations import get_confirmation, DisabledConfirmation, get_confirmation_instance, \
    TelegramConfirmation, ConfirmationBase
from amazon_dash.exceptions import InvalidConfig, ConfirmationError


class GetConfirmationInstance(unittest.TestCase):
    def test_invalid_service(self):
        with self.assertRaises(InvalidConfig):
            get_confirmation_instance({'service': 'foobar'})


class TestGetConfirmation(unittest.TestCase):
    def test_invalid_confirmation_name(self):
        with self.assertRaises(InvalidConfig):
            get_confirmation('', {'confirmation': 'foo'}, {'bar': {}})

    def test_valid_confirmation_name(self):
        cls = get_confirmation('', {'confirmation': 'foo'}, {'foo': {'service': 'disabled'}})
        self.assertIsInstance(cls, DisabledConfirmation)

    def test_multiple_default_confirmations(self):
        with self.assertRaises(InvalidConfig):
            get_confirmation('', {}, {'bar': {'is_default': True}, 'foo': {'is_default': True}})

    def test_default_confirmation(self):
        cls = get_confirmation('', {}, {'foo': {'service': 'disabled', 'is_default': True}})
        self.assertIsInstance(cls, DisabledConfirmation)


class TestConfirmationBase(unittest.TestCase):
    def test_required_fields(self):
        class Confirmation(ConfirmationBase):
            required_fields = ('foo',)
        with self.assertRaises(InvalidConfig):
            Confirmation({})


class TestTelegramConfirmation(unittest.TestCase):
    def get_telegram(self):
        return TelegramConfirmation({'token': 'foo', 'to': 'bar'})

    def test_send(self):
        telegram = self.get_telegram()
        with requests_mock.mock() as m:
            m.post(telegram.url_base.format('foo'), text='{"ok": true}')
            telegram.send('spam')
            self.assertTrue(m.called_once)

    def test_invalid_json(self):
        telegram = self.get_telegram()
        with requests_mock.mock() as m:
            m.post(telegram.url_base.format('foo'), text='{"}invalid')
            with self.assertRaises(ConfirmationError):
                telegram.send('spam')

    def test_send_error(self):
        telegram = self.get_telegram()
        with requests_mock.mock() as m:
            m.post(telegram.url_base.format('foo'), text='{"ok": false}')
            with self.assertRaises(ConfirmationError):
                telegram.send('spam')

    def test_server_error(self):
        telegram = self.get_telegram()
        with requests_mock.mock() as m:
            m.post(telegram.url_base.format('foo'), exc=requests.exceptions.ConnectTimeout)
            with self.assertRaises(ConfirmationError):
                telegram.send('spam')
