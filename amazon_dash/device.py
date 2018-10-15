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


class Device(object):
    """Set the execution method for the device
    """
    execute_instance = None  #: Execute cls instance

    def __init__(self, src, name, actions, config=None):
        """

        :param str src: Mac address
        :param data: device data
        """
        config = config or {}

        if isinstance(src, Device):
            src = src.src
        self.src = src.lower()
        self.name = name or self.src
        self.actions = actions
        self.config = config

    def execute(self, root_allowed=False):
        """Execute this device

        :param bool root_allowed: Only used for ExecuteCmd
        :return: None
        """
        logger.debug('%s device executed (mac %s)', self.name, self.src)
        if not self.execute_instance:
            msg = '%s: There is not execution method in device conf.'
            logger.warning(msg, self.name)
            self.send_confirmation(msg % self.name, False)
            return
        try:
            result = self.execute_instance.execute(root_allowed)
        except Exception as e:
            self.send_confirmation('Error executing the device {}: {}'.format(self.name, e), False)
            raise
        else:
            result = 'The {} device has been started and is running right now'.format(self.name) \
                if result is None else result
            result = result or 'The {} device has been executed successfully'.format(self.name)
            self.send_confirmation(result)
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
