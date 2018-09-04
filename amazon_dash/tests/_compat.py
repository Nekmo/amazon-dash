
try:
    from mock import patch, Mock, mock_open
except ImportError:
    from unittest.mock import patch, Mock, mock_open
