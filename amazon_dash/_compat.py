
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
