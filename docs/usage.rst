.. highlight:: console

=====
Usage
=====
To see the available help run::

    $ amazon-dash --help

Example::

    Usage: amazon-dash [OPTIONS] COMMAND [ARGS]...

    Options:
      --info     set logging to info
      --warning  set logging to warning
      --quiet    set logging to ERROR
      --debug    set logging to DEBUG
      --verbose  set logging to COMM
      --help     Show this message and exit.

    Commands:
      run*          Run server
      check-config  Validate the configuration file.
      discovery     Discover Amazon Dash device on network.
      test-device   Test a configured device without press...


To see the help of a command::

    $ amazon-dash <command> --help

For example::

    $ amazon-dash run --help

    Usage: amazon-dash run [OPTIONS]

      Run server

    Options:
      --config PATH   Path to config file.
      --root-allowed  Allow execute commands on config file as root
      --help          Show this message and exit.


Discovery mode
--------------
Use *discovery mode* **to know the mac of your Dash** (Run the program, and then press the button)::

    $ sudo amazon-dash discovery


Daemon mode
-----------
In daemon mode, it waits for a button to be pressed to execute the associated command. The program will remain running
until the user closes it. Amazon-dash creates a *service* (daemon) file on your system to be able to run the program
easily. The file is copied to your system when you run ``python -m amazon_dash.install``.


Systemd
```````
Most modern Linux systems use Systemd by default. Some exceptions are Slackware and Gentoo. To run amazon-dash using
Systemd::

    $ sudo systemctl start amazon-dash

To check if it has been executed correctly::

    $ sudo systemctl status amazon-dash

.. hint::
    Run ``$ sudo amazon-dash check-config --config /etc/amazon-dash.yml`` to verify that the configuration is correct
    before running amazon-dash

To restart amazon-dash after modifying the configuration file to apply the changes::

      $ sudo systemctl restart amazon-dash

To see the log::

    $ sudo journalctl -r -u amazon-dash

To run Amazon-dash at startup::

    $ sudo systemctl enable amazon-dash



Manually
````````
If your system does not have Systemd or you want to run it manually::

    sudo amazon-dash run[ --root-allowed][ --config amazon-dash.yml]


By default, ``amazon-dash`` will use the ``amazon-dash.yml`` file in the current directory with
``sudo amazon-dash run``. However, you can set the path to the file (for example, ``/etc/amazon-dash.yml``) with
``--config`` parameter. Please note that ``--config`` must be after ``run``.

The default level logging is ``INFO`` but you can change it using the ``--warning``, ``--quiet``, ``--debug`` and
``--verbose`` options. To see on screen every time a button is pressed you need to set the ``--debug`` option.

By default it is forbidden to execute commands as root in your configuration file. This is a security measure to
avoid escalation privileges. If you are going to run amazon-dash as root it is highly recommended to define a
user by each cmd config device. You can disable this security measure using ``--root-allowed``.


Check config
------------
If you have edited the configuration file you can check that the file is ok before starting the program::

    $ sudo amazon-dash check-config --config /etc/amazon-dash.yml


Test device
-----------
Sometimes you may want to test the execution of a device without pressing the associated button. This is useful for
testing and debugging::

    $ sudo amazon-dash test-device <device mac address>[ --root-allowed][ --config <config file>]

For example::

    $ sudo amazon-dash test-device 00:11:22:33:44:55 --config /etc/amazon-dash.yml

