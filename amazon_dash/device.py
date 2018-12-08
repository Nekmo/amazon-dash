from dataclasses import dataclass
from typing import Union

from amazon_dash.action import Action, Actions
from amazon_dash.confirmations import get_confirmation
from amazon_dash.exceptions import InvalidConfig
from amazon_dash.execute import ExecuteCmd, ExecuteUrl, ExecuteHomeAssistant, ExecuteOpenHab, ExecuteIFTTT, logger

EXECUTE_CLS = {
    'cmd': ExecuteCmd,
    'url': ExecuteUrl,
    'homeassistant': ExecuteHomeAssistant,
    'openhab': ExecuteOpenHab,
    'ifttt': ExecuteIFTTT,
}


@dataclass
class Result:
    status: Union[bool, None] = None
    message: str = ''
    exception: Exception = None


class Device(object):
    """Set the execution method for the device
    """
    execute_instance = None  #: Execute cls instance
    on_error = 'fail'

    def __init__(self, src, name, actions, config=None):
        """

        :param str src: Mac address
        :param data: device data
        """
        config = config
        actions = actions or []

        if isinstance(src, Device):
            src = src.src
        self.src = src.lower()
        self.name = name or self.src
        self.actions = Actions(actions, config)
        self.config = config

    def execute(self, root_allowed=False):
        """Execute this device

        :param bool root_allowed: Only used for ExecuteCmd
        :return: None
        """
        logger.debug('%s device executed (mac %s)', self.name, self.src)
        if not self.actions:
            msg = '%s: There is not actions in device conf.'
            logger.warning(msg, self.name)
            # self.send_confirmation(msg % self.name, False)
            return
        success = True
        results = []
        for action in self.actions.get_first_run_actions():
            result = self.execute_action(action, {'mac': self.src})
            success = result.status
            results.append(result)
            if not success and self.on_error == 'fail':
                break
        for action in self.actions.get_complete_actions():
            if action.evaluate_condition('success' if success else 'failure'):
                self.execute_action(action)
        return results

    def execute_action(self, action, params=None):
        result = Result()
        params = params or self.default_params()
        try:
            result.message = action.send(**params)
        # except Exception as e:  # TODO: disabled temporally
        except ImportError as e:
            result.message = 'Error executing the device {} in action {}: {}'.format(self.name, action, e)
            result.exception = e
        else:
            result.status = True
        return result

    def send_confirmation(self, message, success=True):
        """Send success or error message to configured confirmation

        :param str message: Body message to send
        :param bool success: Device executed successfully to personalize message
        :return: None
        """
        message = message.strip()
        if not self.confirmation:
            return
        try:
            self.confirmation.send(message, success)
        except Exception as e:
            logger.warning('Error sending confirmation on device {}: {}'.format(self.name, e))

    def default_params(self):
        return {'mac': self.src}