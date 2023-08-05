import io
import json

from pathlib import Path
from typing import Dict, List

from enderturing import Config
from enderturing.http_client import HttpClient


class Topics:
    """Contains methods for topics.

    Args:
        config (Config): configuration to use.
        client (HttpClient): HTTP client instance to use for requests
    """

    def __init__(self, config: Config, client: HttpClient):
        self._config = config
        self._http_client = client

    def get_topics(self):
        """Gets all topics from the server."""
        return self._http_client.get("/topics")

    def create_topic(self, obj_in):
        """Creates a new topic on the server."""
        return self._http_client.post("/topics", json=obj_in)

    def update_topic(self, topic_id, obj_in):
        """Updates a topic on the server."""
        return self._http_client.put(f"/topics/{topic_id}", json=obj_in)

    def delete_topic(self, topic_id):
        """Deletes a topic from the server."""
        return self._http_client.delete(f"/topics/{topic_id}")

    def do_classification(self, lang, obj_in):
        """Runs the classification on the given data."""
        return self._http_client.put(f"/topics/do-classification?language={lang}", json=obj_in)

    def upload_json(self, *, data: List[Dict] = None, filepath: str = None):
        """Uploads a list of topics to the server."""
        if not data and not filepath:
            raise ValueError("Either data or filepath must be given.")

        if data:
            return self._http_client.post(
                "/topics/json",
                files={"file": ("topics.json", io.StringIO(json.dumps(data)), "application/json")},
            )

        if not Path(filepath).exists():
            raise ValueError(f"File {filepath} does not exist.")

        with open(filepath, "rb") as f:
            return self._http_client.post(
                "/topics/json",
                files={"file": ("topics.json", f, "application/json")},
            )
