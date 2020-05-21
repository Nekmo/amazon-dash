.. highlight:: console

=====
Usage
=====

.. click:: amazon_dash.management:cli
   :prog: amazon-dash
   :show-nested:


Daemon mode
-----------
In daemon mode, it waits for a button to be pressed to execute the associated command. The program will remain running
until the user closes it. Amazon-dash creates a *service* (daemon) file on your system to be able to run the program
easily. The file is copied to your system when you run ``python -m amazon_dash.install``.


Systemd
```````
Most modern Linux systems use Systemd by default. Some exceptions are Slackware and Gentoo. To run amazon-dash using
Systemd::

    sudo systemctl start amazon-dash

To check if it has been executed correctly::

    sudo systemctl status amazon-dash

.. hint::
    Run ``$ sudo amazon-dash check-config --config /etc/amazon-dash.yml`` to verify that the configuration is correct
    before running amazon-dash

To restart amazon-dash after modifying the configuration file to apply the changes::

    sudo systemctl restart amazon-dash

To see the log::

    sudo journalctl -r -u amazon-dash

To run Amazon-dash at startup::

    sudo systemctl enable amazon-dash



Manually
````````
If your system does not have Systemd or you want to run it manually::

    sudo amazon-dash run[ --root-allowed][ --ignore-perms][ --config amazon-dash.yml]


By default, ``amazon-dash`` will use the ``amazon-dash.yml`` file in the current directory with
``sudo amazon-dash run``. However, you can set the path to the file (for example, ``/etc/amazon-dash.yml``) with
``--config`` parameter. Please note that ``--config`` must be after ``run``.

If you run Amazon-dash using root *(necessary to sniff network traffic)* is required to protect the
configuration file **for security reasons)::

    sudo chmod 600 amazon-dash.yml
    sudo chown root:root amazon-dash.yml

If you use Docker you can disable this security measure. using ``--ignore-perms``. It is not recommended to use
this option if you are running Amazon-dash on your machine. It could be used to **scale privileges**.

The default level logging is ``INFO`` but you can change it using the ``--warning``, ``--quiet``, ``--debug`` and
``--verbose`` options. To see on screen every time a button is pressed you need to set the ``--debug`` option.

By default it is forbidden to execute commands as root in your configuration file. This is a security measure to
avoid escalation privileges. If you are going to run amazon-dash as root it is highly recommended to define a
user by each cmd config device. You can disable this security measure using ``--root-allowed``.

