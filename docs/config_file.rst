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

Execute cmd
-----------
When the **cmd execution method** is used, the following options are available.

* **user**: System user that will execute the command. This option can only be used if Amazon-Dash is running as root.
* **cwd**: Directory in which the command will be executed.

Call url
--------
When the **url execution method** is used, the following options are available.

* **method**: HTTP method. By default GET.
* **headers**: Headers to send to server. Content-Type will be overwritten if it is defined later.
* **content-type** (*): HTTP Content-Type Header. Only available if Body is defined. If body is defined, default is form.
* **body**: Request payload. Only if the method is POST/PUT/PATCH. In json or form mode, the content must be a valid json. It is recommended to use single quotes before and after content in json.

(*) Content type aliases: `form = application/x-www-form-urlencoded`. `json = application/json`. `plain = text/plain`.

Homeassistant event
-------------------
When the **homeassistant execution method** is used, the following options are available.

* **event** (required): Event name to send.
* **data**: Event data to send. Use json as string.

Example
-------
The following example is available in /etc/amazon-dash.yml when installed:

.. literalinclude:: ../amazon_dash/install/amazon-dash.yml

