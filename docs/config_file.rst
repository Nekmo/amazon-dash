.. highlight:: console

===========
Config file
===========

The configuration file can be found anywhere but if the program runs in root mode,
it is necessary that only root can modify the file. This is a security measure to prevent
someone from executing commands as root using the program.

To change the permissions::

    sudo chmod 600 amazon-dash.yml
    sudo chown root:root amazon-dash.yml

The amazon-dash system configuration file is located in: ``/etc/amazon-dash.yml``

.. important::
    Remember to restart the service whenever you make a change to apply it.
    If you are using systemd, restart the service using ``systemctl restart amazon-dash``

Example
-------
The following example is available in ``/etc/amazon-dash.yml`` when installed:

.. literalinclude:: ../amazon_dash/install/amazon-dash.yml

Real example:

.. code-block:: yaml

    # amazon-dash.yml
    # ---------------
    settings:
      delay: 10
    devices:
      0C:47:C9:98:4A:12:
        name: Hero
        user: nekmo
        cmd: spotify
      AC:63:BE:67:B2:F1:
        name: Kit Kat
        url: 'http://domain.com/path/to/webhook'
        method: post
        content-type: json
        body: '{"mac": "AC:63:BE:67:B2:F1", "action": "toggleLight"}'
        confirmation: send-tg
      40:B4:CD:67:A2:E1:
        name: Fairy
        homeassistant: hassio.local
        event: toggle_kitchen_light
      18:74:2E:87:01:F2:
        name: Doritos
        openhab: 192.168.1.140
        item: open_door
        state: "ON"
    confirmations:
      send-tg:
        service: telegram
        token: '402642618:QwGDgiKE3LqdkNAtBkq0UEeBoDdpZYw8b4h'
        to: 24291592
        is_default: false


Common options
--------------
The syntax of the configuration file is yaml. The configuration file has 3 main sections:

* **settings** (optional): common options.
* **devices** (required): The amazon dash devices.
* **confirmations** (optional): confirmation on device executed.


settings section
~~~~~~~~~~~~~~~~
The following options are available in **settings**:

* **delay** (optional): On seconds. By default, 10 seconds. Minimum time that must pass between pulsations of the
  Amazon Dash button.

Device section
~~~~~~~~~~~~~~
Each **device** is identified by the button **mac**. The mac can be obtained with the discovery command.
In the configuration of each button, there may be a way of execution. Only one execution method is allowed
for each device. The available exection methods are:

* **cmd**: local command line command. Arguments can be placed after the command.
* **url**: Call a url.
* **homeassistant**: send event to Homeassistant. This argument must be the address to the hass server (protocol and
  port are optional. By default http and 8123, respectively).
* **openhab**: send event to OpenHAB. This argument must be the address to the hass server (protocol and
  port are optional. By default http and 8080, respectively).

The devices can also have **these common options**:

* **name**: device name for log messages.
* **confirmation**: confirmation to use on device execution.


A device example:

.. code-block:: yaml

    # amazon-dash.yml
    # ---------------
    settings:
      delay: 10
    devices:
      0C:47:C9:98:4A:12:
        name: Hero
        user: nekmo
        cmd: spotify


Confirmation section
~~~~~~~~~~~~~~~~~~~~
Send a **confirmation after running a device**. Send a message whether the execution is successful or if it fails. If
the execution returns an output this will be the message that is sent.

Each confirmation has **a name** to be able to use it on the devices (on the example ``confirmation-name``):

.. code-block:: yaml

    # amazon-dash.yml
    # ---------------
    settings:
      delay: 10
    devices:
      AC:63:BE:67:B2:F1:
        name: Kit Kat
        url: 'http://domain.com/path/to/webhook'
        confirmation: confirmation-name
    confirmations:
      confirmation-name:
        service: telegram
        token: '402642618:QwGDgiKE3LqdkNAtBkq0UEeBoDdpZYw8b4h'
        to: 24291592

For run a confirmation for all devices by default using ``is_default: true``:

.. code-block:: yaml

    # amazon-dash.yml
    # ---------------
    settings:
      delay: 10
    devices:
      # ...
    confirmations:
      confirmation-name:
        service: telegram
        token: '402642618:QwGDgiKE3LqdkNAtBkq0UEeBoDdpZYw8b4h'
        to: 24291592
        is_default: true


Execution
---------
The devices section allows you to perform an action when you press an Amazon dash button.
The following execution methods are available.


Execute cmd
~~~~~~~~~~~
When the **cmd execution method** is used, the following options are available.

* **user**: System user that will execute the command. This option can only be used if Amazon-Dash is running as root.
* **cwd**: Directory in which the command will be executed.

Example:

.. code-block:: yaml

    # amazon-dash.yml
    # ---------------
    settings:
      delay: 10
    devices:
      0C:47:C9:98:4A:12:
        name: Hero
        user: nekmo
        cmd: spotify


Call url
~~~~~~~~
When the **url execution method** is used, the following options are available.

* **method**: HTTP method. By default GET.
* **headers**: Headers to send to server. Content-Type will be overwritten if it is defined later.
* **content-type** (*): HTTP Content-Type Header. Only available if Body is defined. If body is defined, default is form.
* **body**: Request payload. Only if the method is POST/PUT/PATCH. In json or form mode, the content must be a valid json. It is recommended to use single quotes before and after content in json.

(*) Content type aliases: `form = application/x-www-form-urlencoded`. `json = application/json`. `plain = text/plain`.


Example:

.. code-block:: yaml

    # amazon-dash.yml
    # ---------------
    settings:
      delay: 10
    devices:
      AC:63:BE:67:B2:F1:
        name: Kit Kat
        url: 'http://domain.com/path/to/webhook'
        method: post
        content-type: json
        body: '{"mac": "AC:63:BE:67:B2:F1", "action": "toggleLight"}'
        confirmation: send-tg


Homeassistant event
~~~~~~~~~~~~~~~~~~~
When the **homeassistant execution method** is used, the following options are available.

* **event** (required): Event name to send.
* **data**: Event data to send. Use json as string.

Example:

.. code-block:: yaml

    # amazon-dash.yml
    # ---------------
    settings:
      delay: 10
    devices:
      40:B4:CD:67:A2:E1:
        name: Fairy
        homeassistant: hassio.local
        event: toggle_kitchen_light


OpenHAB event
~~~~~~~~~~~~~
When the **openhab execution method** is used, the following options are available.

* **item** (required): Open Hab item to send.
* **state**: State to send. On switch items ON/OFF. ON by default. The state must be between quotes.


Example:

.. code-block:: yaml

    # amazon-dash.yml
    # ---------------
    settings:
      delay: 10
    devices:
      18:74:2E:87:01:F2:
        name: Doritos
        openhab: 192.168.1.140
        item: open_door
        state: "ON"


Confirmations
-------------
The following **services** are supported to send confirmation messages.

Telegram
~~~~~~~~
For use a telegram service you need to define:

* **token**: get your own token for your bot using ``/newbot`` on `@BotFather <https://t.me/botfather>`_.
* **to**: your telegram id. You can get it using `@get_id_bot <https://t.me/get_id_bot>`_ or other method.

After create a bot, you need to start a conversation with your bot. Bots can not send messages to users if people
have not started a conversation before.

.. code-block:: yaml

    # amazon-dash.yml
    # ---------------
    settings:
      delay: 10
    devices:
      # ...
    confirmations:
      send-tg:
        service: telegram
        token: '402642618:QwGDgiKE3LqdkNAtBkq0UEeBoDdpZYw8b4h'
        to: 24291592
        is_default: false
