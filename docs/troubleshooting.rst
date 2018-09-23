Troubleshooting
===============

Requirements and installation
-----------------------------
All dependencies are commonly used on a Linux system, but some may not be installed on your system. The dependencies
are:

* Python 2.7 or 3.4+.
* Python-pip (pip).
* Tcpdump.
* Sudo

Amazon-dash v2.0.0 will only be compatible with Python 3.6+. This version is currently in development.


Why root is required
--------------------
This program needs permission to open raw sockets on your system. You can set this permission using setcap, but you
must be very careful about who can run the program. Raw sockets permission could allow scaling permissions on the
system::

    setcap cap_net_raw=eip ./scripts/amazon-dash
    setcap cap_net_raw=eip /usr/bin/pythonX.X
    setcap cap_net_raw=eip /usr/bin/tcpdump

http://stackoverflow.com/questions/36215201/python-scapy-sniff-without-root


Amazon Dash Exceptions
----------------------
These are the types of errors that are contemplated in Amazon Dash. If Amazon Dash returns one of these errors, please
do not open an issue without reading the error message. The following is an example of a configuration error::

    $ amazon-dash run
    Welcome to Amazon-dash v0.4.1-1 using Python 3.6.3
    Listening for events. Amazon-dash will execute the events associated with the registered buttons.
    [Error] Amazon Dash Exception (InvalidConfig):
    The configuration file is invalid (/current/path/amazon-dash.yml). Check the file and read the documentation.
    while scanning a simple key
      in "amazon-dash.yml", line 42, column 5
    could not find expected ':'
      in "amazon-dash.yml", line 43, column 1

The line number with the typo appears in the error. The error type is in parentheses (in the ex. *InvalidConfig*). These
are the types of errors:


.. automodule:: amazon_dash.exceptions
    :members:


Cli errors
----------
The command line will return an error if unknown or misused options are used. For example::

    $ amazon-dash foobarspam
    Welcome to Amazon-dash v0.4.1-1 using Python 3.6.3
    Usage: amazon-dash foobarspam [OPTIONS]

    Error: Got unexpected extra argument (foobarspam)

Obviously *foobarspam* is not a known command. Please use ``--help`` to see all the commands.


The problem is the same with the options. For example::

    $ amazon-dash --foo
    Welcome to Amazon-dash v0.4.1-1 using Python 3.6.3
    Error: no such option: --foo

The command line exceptions (like abort) on Click return an ``1`` error code. Errors due to misuse of the options
return an error code ``2``.



Installation errors
-------------------
If you have problems with the installation, check that you meet all the requirements of section
`Requirements and installation`_. Check that you are running the commands **as sudo**. If you still have problems
open a ticket and do not forget to paste all the error messages during the installation.

To verify that you have installed Amazon Dash and you are using the latest version::

    $ amazon-dash --version
    You are running Amazon-dash v0.4.1-1 using Python 3.6.3.
    There is a new version available: 0.4.2. Upgrade it using: sudo pip install -U amazon-dash
    Installation path: /home/nekmo/Workspace/amazon-dash/amazon_dash
    Current path: /home/nekmo/Workspace/amazon-dash

