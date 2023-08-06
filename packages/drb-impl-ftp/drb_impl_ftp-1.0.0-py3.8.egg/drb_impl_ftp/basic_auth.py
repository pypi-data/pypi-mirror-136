class BasicAuth:
    """
    This class allow us to use basic auth (with username password) to connect
    to the ftp server you aim.
    """
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
