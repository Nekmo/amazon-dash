
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
