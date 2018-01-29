.. highlight:: shell

=====
Usage
=====
To see the available help run::

    $ amazon-dash --help

Example::

    usage: amazon-dash [-h] [--config CONFIG] [--warning] [--quiet] [--debug]
                       [--verbose]
                       {discovery,run} ...

    Amazon Dash.

    positional arguments:
      {discovery,run}
        discovery      Discover Amazon Dash device on network.
        run            Run server

    optional arguments:
      -h, --help       show this help message and exit
      --config CONFIG  Path to config file.
      --warning        set logging to warning
      --quiet          set logging to ERROR
      --debug          set logging to DEBUG
      --verbose        set logging to COMM


Discovery mode
--------------
Use *discovery mode* **to know the mac of your Dash** (Run the program, and then press the button)::

    $ sudo amazon-dash discovery


Daemon mode
-----------
In daemon mode, it waits for a button to be pressed to execute the associated command.

.. code::

    sudo amazon-dash[ --config amazon-dash.yml] run


By default, ``amazon-dash`` will use the ``amazon-dash.yml`` file in the current directory with
``sudo amazon-dash run``. However, you can set the path to the file (for example, ``/etc/amazon-dash.yml``) with
``--config`` parameter. Please note that ``--config`` must be before ``run``.

The default level logging is ``INFO`` but you can change it using the ``--warning``, ``--quiet``, ``--debug`` and
``--verbose`` options. To see on screen every time a button is pressed you need to set the ``--debug`` option.

By default it is forbidden to execute commands as root in your configuration file. This is a security measure to
avoid escalation privileges. If you are going to run amazon-dash as root it is highly recommended to define a
user by each cmd config device. You can disable this security measure using ``--root-allowed``.
