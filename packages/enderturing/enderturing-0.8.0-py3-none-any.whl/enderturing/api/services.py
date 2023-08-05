from enderturing import Config
from enderturing.http_client import HttpClient


class Services:
    def __init__(self, config: Config, client: HttpClient):
        """
        Args:
            config (Config): configuration to use.
            client (HttpClient): HTTP client instance to use for requests
        """
        self._config = config
        self._http_client = client

    def get_instances(self):
        """Gets a list of active (downloaded and activated) services"""
        return self._http_client.get("/services")

    def get_status(self):
        """Gets all statuses"""
        return self._http_client.get("/services/status")

    def get_service_status(self, name):
        """Gets a services status"""
        return self._http_client.get(f"/services/{name}/status")
