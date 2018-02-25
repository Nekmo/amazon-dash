import unittest

from amazon_dash.confirmations import get_confirmation, DisabledConfirmation, get_confirmation_instance
from amazon_dash.exceptions import InvalidConfig


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
