from enderturing import Config
from enderturing.http_client import HttpClient


class Filters:
    """Contains methods for filters.

    Args:
        config (Config): configuration to use.
        client (HttpClient): HTTP client instance to use for requests
    """

    def __init__(self, config: Config, client: HttpClient):
        self._config = config
        self._http_client = client

    def get_filters(self):
        """Gets list of filters"""
        return self._http_client.get("/filters")

    def create_filter(self, obj_in):
        """Creates a new filter"""
        return self._http_client.post("/filters", json=obj_in)
