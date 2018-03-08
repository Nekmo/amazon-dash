===========
Config file
===========

The configuration file can be found anywhere but if the program runs in root mode,
it is necessary that only root can modify the file. This is a security measure to prevent
someone from executing commands as root using the program.

To change the permissions::

    sudo chmod 600 amazon-dash.yml
    sudo chown root:root amazon-dash.yml


Common options
--------------
The syntax of the configuration file is yaml. The configuration file has 2 main sections:

* **settings** (optional): common options.
* **devices** (required): The amazon dash devices.
* **confirmations** (optional): confirmation on device executed.

The following options are available in **settings**:

* **delay** (optional): On seconds. By default, 10 seconds. Minimum time that must pass between pulsations of the
  Amazon Dash button.

Each device is identified by the button **mac**. The mac can be obtained with the discovery command.
In the configuration of each button, there may be a way of execution. Only one execution method is allowed
for each device. The available exection methods are:

* **cmd**: local command line command. Arguments can be placed after the command.
* **url**: Call a url.
* **homeassistant**: send event to Homeassistant. This argument must be the address to the hass server (protocol and
  port are optional. By default http and 8123, respectively).

The devices can also have **these common options**:

* **name**: device name for log messages.
* **confirmation**: confirmation to use on device execution.


Execution
---------
The devices section allows you to perform an action when you press an Amazon dash button.

Execute cmd
~~~~~~~~~~~
When the **cmd execution method** is used, the following options are available.

* **user**: System user that will execute the command. This option can only be used if Amazon-Dash is running as root.
* **cwd**: Directory in which the command will be executed.

Call url
~~~~~~~~
When the **url execution method** is used, the following options are available.

* **method**: HTTP method. By default GET.
* **headers**: Headers to send to server. Content-Type will be overwritten if it is defined later.
* **content-type** (*): HTTP Content-Type Header. Only available if Body is defined. If body is defined, default is form.
* **body**: Request payload. Only if the method is POST/PUT/PATCH. In json or form mode, the content must be a valid json. It is recommended to use single quotes before and after content in json.

(*) Content type aliases: `form = application/x-www-form-urlencoded`. `json = application/json`. `plain = text/plain`.

Homeassistant event
~~~~~~~~~~~~~~~~~~~
When the **homeassistant execution method** is used, the following options are available.

* **event** (required): Event name to send.
* **data**: Event data to send. Use json as string.


Confirmations
-------------
Send a **confirmation after running a device**. Send a message whether the execution is successful or if it fails. If
the execution returns an output this will be the message that is sent.

Each confirmation has **a name** to be able to use it on the devices (on the example ``confirmation-name``)::

    confirmations:
      confirmation-name:
        service: telegram
        token: '402642618:QwGDgiKE3LqdkNAtBkq0UEeBoDdpZYw8b4h'
        to: 24291592
    devices:
      AC:63:BE:67:B2:F1:
        name: Kit Kat
        url: 'http://domain.com/path/to/webhook'
        confirmation: confirmation-name

For run a confirmation for all devices by default using ``is_default: true``::

    confirmations:
      confirmation-name:
        service: telegram
        token: '402642618:QwGDgiKE3LqdkNAtBkq0UEeBoDdpZYw8b4h'
        to: 24291592
        is_default: true


Telegram
~~~~~~~~
For use a telegram service you need to define:

* **token**: get your own token for your bot using ``/newbot`` on `@BotFather <https://t.me/botfather>`_.
* **to**: your telegram id. You can get it using `@get_id_bot <https://t.me/get_id_bot>`_ or other method.

After create a bot, you need to start a conversation with your bot. Bots can not send messages to users if people
have not started a conversation before.

Example
-------
The following example is available in /etc/amazon-dash.yml when installed:

.. literalinclude:: ../amazon_dash/install/amazon-dash.yml

Real example::

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
    confirmations:
      send-tg:
        service: telegram
        token: '402642618:QwGDgiKE3LqdkNAtBkq0UEeBoDdpZYw8b4h'
        to: 24291592
        is_default: false
