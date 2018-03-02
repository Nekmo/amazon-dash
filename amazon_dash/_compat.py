import sys

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


if sys.version_info > (3,2):
    import subprocess
else:
    import subprocess32 as subprocess
