.. highlight:: console

Upgrade
=======
If you use an earlier version of Amazon Dash you may need to make changes to your configuration.

To update to the latest version use::

    $ sudo pip install -U amazon-dash  # and after:
    $ sudo python -m amazon_dash.install


Versions before 1.0.0
---------------------
The order of the parameter ``--config`` in version 1.0.0 has changed.

Before 1.0.0 release this parameter had to be BEFORE the command to be used::

    $ sudo amazon-dash --config amazon-dash.yml run

After version 1.0.0 this parameter must be defined AFTER the command::

    $ sudo amazon-dash run --config amazon-dash.yml

If you use the systemd service it is necessary to modify the service file manually::

Edit the file ``/usr/lib/systemd/system/amazon-dash.service`` or ``/lib/systemd/system/amazon-dash.service`` (depending
on your system).

You must change the file from this:

.. code-block:: ini

    [Unit]
    Description=Amazon Dash service

    [Service]
    User=root
    ExecStart=/usr/bin/env amazon-dash --config /etc/amazon-dash.yml run
    Restart=always
    RestartSec=3

    [Install]
    WantedBy=multi-user.target


To this:

.. code-block:: ini

    [Unit]
    Description=Amazon Dash service

    [Service]
    User=root
    ExecStart=/usr/bin/env amazon-dash run --config /etc/amazon-dash.yml
    Restart=always
    RestartSec=3

    [Install]
    WantedBy=multi-user.target
