from enderturing import Config
from enderturing.http_client import HttpClient


class Scorecard:
    """Contains methods for scorecards data access.

    Args:
        config (Config): configuration to use.
        client (HttpClient): HTTP client instance to use for requests
    """

    def __init__(self, config: Config, client: HttpClient):
        self._config = config
        self._http_client = client

    def get_scorecards(self):
        """Gets all scorecards"""
        return self._http_client.get("/scorecards")

    def create_scorecard(self, obj_in):
        """Creates a new scorecard"""
        return self._http_client.post("/scorecards", json=obj_in)

    def get_scorecard(self, pk):
        """Gets specific scorecard"""
        return self._http_client.get(f"/scorecards/{pk}")

    def update_scorecard(self, pk, obj_in):
        """Updates existing scorecard"""
        return self._http_client.put(f"/scorecards/{pk}", obj_in)

    def delete_scorecard(self, pk):
        return self._http_client.delete(f"/scorecards/{pk}")
