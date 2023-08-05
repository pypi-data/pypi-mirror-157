from enderturing import Config
from enderturing.http_client import HttpClient


class Connectors:
    def __init__(self, config: Config, client: HttpClient):
        """
        Args:
            config (Config): configuration to use.
            client (HttpClient): HTTP client instance to use for requests
        """
        self._config = config
        self._http_client = client

    def get_instances(self):
        """Gets list of all connectors"""
        return self._http_client.get("/connectors")

    def create_instance(self, obj_in):
        """Creates a new connector"""
        return self._http_client.post("/connectors", json=obj_in)

    def get_status(self):
        """Gets a status of all connectors"""
        return self._http_client.get("/connectors/status")

    def get_types(self):
        """Gets types of all connectors"""
        return self._http_client.get("/connectors/types")

    def get_versions(self):
        """Gets versions of all connectors"""
        return self._http_client.get("/connectors/versions")

    def get_instance(self, pk):
        """Gets a single connector"""
        return self._http_client.get(f"/connectors/{pk}")

    def update_instance(self, pk, obj_in):
        """Updates a single connector"""
        return self._http_client.put(f"/connectors/{pk}", json=obj_in)

    def delete_instance(self, pk):
        """Deletes a connector"""
        return self._http_client.delete(f"/connectors/{pk}")

    def get_instance_status(self, pk):
        """Gets a status of a specific connector"""
        return self._http_client.get(f"/connectors/{pk}/status")
