import requests
from requests import RequestException

from amazon_dash.exceptions import InvalidConfig, ConfirmationError
from amazon_dash._compat import JSONDecodeError

class ConfirmationBase(object):
    name = None
    required_fields = ()

    def __init__(self, data):
        for key in self.required_fields:
            if key not in data:
                raise InvalidConfig(extra_body='{} is a required parameter for {} confirmation'.format(key, self.name))
        self.data = data

    def send(self, message, success=True):
        raise NotImplementedError


class DisabledConfirmation(ConfirmationBase):
    name = 'disabled'

    def send(self, message, success=True):
        pass


class TelegramConfirmation(ConfirmationBase):
    url_base = 'https://api.telegram.org/bot{}/sendMessage'
    name = 'telegram'
    required_fields = ('token', 'to')

    def send(self, message, success=True):
        try:
            r = requests.post(self.url_base.format(self.data['token']), dict(
                text=message, chat_id=self.data['to'],
            ))
        except RequestException as e:
            raise ConfirmationError('Unable to connect to Telegram servers on telegram confirmation: {}'.format(e))
        try:
            data = r.json()
        except JSONDecodeError:
            raise ConfirmationError('Invalid JSON response in telegram confirmation (server error?)')
        if not data.get('ok'):
            raise ConfirmationError('Error on telegram confirmation. Error code: {}. Error message: {}'.format(
                data.get('error_code'), data.get('description')
            ))


class PushbulletConfirmation(ConfirmationBase):
    url_base = 'https://api.pushbullet.com/v2/pushes'
    name = 'pushbullet'
    required_fields = ('token',)
    one_field_of = {'device_iden', 'email', 'channel_tag', 'client_id'}
    to_field = None

    def __init__(self, data):
        one_fields = set(data) & self.one_field_of
        if len(one_fields) > 1:
            raise InvalidConfig(extra_body='Only one in {} is required for {} notifications'.format(
                ', '.join(one_fields), self.name))
        elif one_fields:
            self.to_field = one_fields.pop()
        super(PushbulletConfirmation, self).__init__(data)

    def get_data(self, body, title=''):
        data = {
            "type": "note",
            "body": body,
        }
        if title:
            data["title"] = title
        if self.to_field:
            data[self.to_field] = self.data[self.to_field]
        return data

    def send(self, message, success=True):
        try:
            r = requests.post(self.url_base, json=self.get_data(message),
                              headers={'Access-Token': self.data['token']})
        except RequestException as e:
            raise ConfirmationError('Unable to connect to Pushbullet servers on pushbullet confirmation: {}'.format(e))
        try:
            r.json()
        except JSONDecodeError:
            raise ConfirmationError('Invalid JSON response in pushbullet confirmation (server error?)')


CONFIRMATIONS = {
    'telegram': TelegramConfirmation,
    'pushbullet': PushbulletConfirmation,
    'disabled': DisabledConfirmation,
}


def get_confirmation_instance(confirmation_data):
    confirmation_data = confirmation_data.copy()
    if confirmation_data.get('service') not in CONFIRMATIONS:
        raise InvalidConfig(extra_body='{} is a invalid confirmation service')
    return CONFIRMATIONS[confirmation_data.pop('service')](confirmation_data)


def get_confirmation(device_id, device_data, confirmations):
    name = device_data.get('confirmation')
    if name and name not in confirmations:
        raise InvalidConfig(extra_body='{} is not a registered confirmation config on {} device'.format(name,
                                                                                                        device_id))
    if name:
        return get_confirmation_instance(confirmations[name])
    defaults = list(filter(lambda x: x.get('is_default'), confirmations.values()))
    if len(defaults) > 1:
        raise InvalidConfig(extra_body='Multiple default confirmations. There can be only one.')
    if defaults:
        return get_confirmation_instance(defaults[0])
