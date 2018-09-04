
try:
    from mock import patch, Mock, mock_open
except ImportError:
    # Python<3.6 support
    from unittest.mock import patch, Mock, mock_open
