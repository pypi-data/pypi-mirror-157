from enderturing import Config
from enderturing.http_client import HttpClient


class System:
    def __init__(self, config: Config, client: HttpClient):
        """
        Args:
            config (Config): configuration to use.
            client (HttpClient): HTTP client instance to use for requests
        """
        self._config = config
        self._http_client = client

    def get_update(self):
        """Gets a system update status"""
        return self._http_client.get("/system/update")

    def update_check(self):
        """Runs versionAPI check"""
        return self._http_client.put("/system/update/check")

    def get_license(self):
        """Gets a license data"""
        return self._http_client.get("/system/license")
