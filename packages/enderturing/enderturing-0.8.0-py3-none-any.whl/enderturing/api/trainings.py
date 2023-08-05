from enderturing import Config
from enderturing.http_client import HttpClient


class Trainings:
    def __init__(self, config: Config, client: HttpClient):
        """
        Args:
            config (Config): configuration to use.
            client (HttpClient): HTTP client instance to use for requests
        """
        self._config = config
        self._http_client = client

    def get_my_trainings(self):
        return self._http_client.get("/trainings/users/me")

    def get_user_trainings(self, user_id):
        return self._http_client.get(f"/trainings/users/{user_id}")

    def add_task(self, task_id, session_id):
        """Add session to task"""
        return self._http_client.post(f"/trainings/{task_id}/sessions/{session_id}")

    def add_trainings(self, obj_in):
        return self._http_client.post("/trainings", json=obj_in)

    def delete_task(self, task_id):
        return self._http_client.delete(f"/trainings/{task_id}")
