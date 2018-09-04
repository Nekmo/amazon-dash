
try:
    from json import JSONDecodeError
except ImportError:
    # Python<3.5 support
    JSONDecodeError = ValueError
