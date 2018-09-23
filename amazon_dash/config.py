from __future__ import print_function
import os
import stat
from grp import getgrgid
from pwd import getpwuid

from jsonschema import validate, ValidationError
from yaml import load
from yaml.error import YAMLError

from amazon_dash.exceptions import SecurityException, ConfigFileNotFoundError, InvalidConfig

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

#: Json-schema validation
SCHEMA = {
    "title": "Config",
    "type": "object",
    "properties": {
        "settings": {
            "type": "object",
            "properties": {
                "delay": {
                    "type": "integer"
                },
                "interface": {
                    "type": "string"
                },
            }
        },
        "devices": {
            "type": "object",
            "properties": {
                "/": {}
            },
            "patternProperties": {
                "^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "cmd": {
                            "type": "string"
                        },
                        "user": {
                            "type": "string",
                        },
                        "cwd": {
                            "type": "string",
                        },
                        "url": {
                            "type": "string"
                        },
                        "method": {
                            "type": "string",
                            "oneOf": [
                                {"pattern": "GET|get"},
                                {"pattern": "HEAD|head"},
                                {"pattern": "POST|post"},
                                {"pattern": "PUT|put"},
                                {"pattern": "DELETE|delete"},
                                {"pattern": "CONNECT|connect"},
                                {"pattern": "OPTIONS|options"},
                                {"pattern": "trace|trace"},
                                {"pattern": "PATCH|patch"},
                            ]
                        },
                        "headers": {
                            "type": "object",
                        },
                        "content-type": {
                            "type": "string"
                        },
                        "body": {
                            "type": "string"
                        },
                        "homeassistant": {
                            "type": "string"
                        },
                        "ifttt": {
                            "type": "string"
                        },
                        "event": {
                            "type": "string"
                        },
                        "confirmation": {
                            "type": "string",
                        }
                    },
                }
            },
            "additionalProperties": False,

        },
        "confirmations": {
            "type": "object",
            "properties": {
                "/": {}
            },
            "patternProperties": {
                "^.+$": {
                    "type": "object",
                    "properties": {
                        "service": {
                            "enum": [
                                'telegram',
                                'pushbullet',
                            ]
                        },
                        "token": {
                            "type": "string",
                        },
                        "is_default": {
                            "type": "boolean",
                        },
                        "to": {
                            "type": "integer"
                        }
                    },
                    "required": ["service"],
                }
            },
        }
    },
    "required": ["devices"]
}


def get_file_owner(file):
    """Get file owner id

    :param str file: Path to file
    :return: user id
    :rtype: int
    """
    try:
        return getpwuid(os.stat(file).st_uid)[0]
    except KeyError:
        return '???'


def get_file_group(file):
    """Get file group id

    :param file: Path to file
    :return: group id
    :rtype: int
    """
    try:
        return getgrgid(os.stat(file).st_uid)[0]
    except KeyError:
        return '???'


def bitperm(s, perm, pos):
    """Returns zero if there are no permissions for a bit of the perm. of a file. Otherwise it returns a positive value

    :param os.stat_result s: os.stat(file) object
    :param str perm: R (Read) or W (Write) or X (eXecute)
    :param str pos: USR (USeR) or GRP (GRouP) or OTH (OTHer)
    :return: mask value
    :rtype: int
    """
    perm = perm.upper()
    pos = pos.upper()
    assert perm in ['R', 'W', 'X']
    assert pos in ['USR', 'GRP', 'OTH']
    return s.st_mode & getattr(stat, 'S_I{}{}'.format(perm, pos))


def oth_w_perm(file):
    """Returns True if others have write permission to the file

    :param str file: Path to file
    :return: True if others have permits
    :rtype: bool
    """
    return bitperm(os.stat(file), 'w', 'oth')


def only_root_write(path):
    """File is only writable by root

    :param str path: Path to file
    :return: True if only root can write
    :rtype: bool
    """
    s = os.stat(path)
    for ug, bp in [(s.st_uid, bitperm(s, 'w', 'usr')), (s.st_gid, bitperm(s, 'w', 'grp'))]:
        # User id (is not root) and bit permission
        if ug and bp:
            return False
    if bitperm(s, 'w', 'oth'):
        return False
    return True


class Config(dict):
    """Parse and validate yaml Amazon-dash file config. The instance behaves like a dictionary
    """
    def __init__(self, file, ignore_perms=False, **kwargs):
        """Set the config file and validate file permissions

        :param str file: path to file
        :param kwargs: default values in dict
        """
        super(Config, self).__init__(**kwargs)
        if not os.path.lexists(file):
            raise ConfigFileNotFoundError(file)
        if not ignore_perms and ((not os.getuid() and not only_root_write(file)) or oth_w_perm(file)):
            file = os.path.abspath(file)
            raise SecurityException(
                'There should be no permissions for other users in the file "{file}". '
                'Current permissions: {user}:{group} {perms}. {msg}. '
                'Run "sudo chmod 660 \'{file}\' && sudo chown root:root \'{file}\'"'.format(
                    file=file, user=get_file_owner(file),
                    group=get_file_group(file), perms=os.stat(file).st_mode & 0o777,
                    msg='Removes write permission for others' if os.getuid()
                    else 'Only root must be able to write to file'))
        self.file = file
        self.read()

    def read(self):
        """Parse and validate the config file. The read data is accessible as a dictionary in this instance

        :return: None
        """
        try:
            data = load(open(self.file), Loader)
        except (UnicodeDecodeError, YAMLError) as e:
            raise InvalidConfig(self.file, '{}'.format(e))
        try:
            validate(data, SCHEMA)
        except ValidationError as e:
            raise InvalidConfig(self.file, e)
        self.update(data)


def check_config(file, printfn=print):
    """Command to check configuration file. Raises InvalidConfig on error

    :param str file: path to config file
    :param printfn: print function for success message
    :return: None
    """
    Config(file).read()
    printfn('The configuration file "{}" is correct'.format(file))
