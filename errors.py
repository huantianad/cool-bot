class Error(Exception):
    """Base error"""
    pass


class ConfigError(Error):
    """Error for config"""

    def __init__(self, message):
        self.message = message
