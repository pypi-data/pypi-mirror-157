from enderturing import Config
from enderturing.http_client import HttpClient


class Triggers:
    def __init__(self, config: Config, client: HttpClient):
        """
        Args:
            config (Config): configuration to use.
            client (HttpClient): HTTP client instance to use for requests
        """
        self._config = config
        self._http_client = client

    def get_triggers(self):
        """Gets a list of triggers"""
        return self._http_client.get("/triggers")

    def create_trigger(self, obj_in):
        """Creates a new trigger"""
        return self._http_client.post("/triggers", json=obj_in)

    def read_sources(self):
        """Gets a list of sources"""
        return self._http_client.get("/triggers/sources")

    def get_instance(self, id):
        """Gets a single trigger"""
        return self._http_client.get(f"/triggers/{id}")

    def update_instance(self, id, obj_in):
        """Updates a single trigger"""
        return self._http_client.put(f"/triggers/{id}", json=obj_in)

    def delete_instance(self, id):
        """Deletes a trigger"""
        return self._http_client.delete(f"/triggers/{id}")
