from enderturing import Config
from enderturing.http_client import HttpClient


class Users:
    def __init__(self, config: Config, client: HttpClient):
        """
        Args:
            config (Config): configuration to use.
            client (HttpClient): HTTP client instance to use for requests
        """
        self._config = config
        self._http_client = client

    def get_me(self):
        """Get current user data"""
        return self._http_client.get("/users/me")
