from enderturing import Config
from enderturing.http_client import HttpClient


class Hashtags:
    """Contains methods for hashtags.

    Args:
        config (Config): configuration to use.
        client (HttpClient): HTTP client instance to use for requests
    """

    def __init__(self, config: Config, client: HttpClient):
        self._config = config
        self._http_client = client

    def get_tags(self, prefix):
        """Gets a tag from prefix"""
        return self._http_client.get(f"/hashtags?prefix={prefix}")

    def create_tag(self, obj_in):
        """Creates a new tags"""
        return self._http_client.post("/hashtags", json=obj_in)
