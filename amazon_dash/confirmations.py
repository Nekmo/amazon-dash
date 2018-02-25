from amazon_dash.exceptions import InvalidConfig


class ConfirmationBase(object):
    def __init__(self, data):
        self.data = data


class DisabledConfirmation(ConfirmationBase):
    pass


class TelegramConfirmation(ConfirmationBase):
    pass


CONFIRMATIONS = {
    'telegram': TelegramConfirmation,
    'disabled': DisabledConfirmation,
}


def get_confirmation_instance(confirmation_data):
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
