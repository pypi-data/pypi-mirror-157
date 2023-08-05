import io
import json

from pathlib import Path
from typing import Dict, List

from enderturing import Config
from enderturing.http_client import HttpClient


class Agent:
    """Contains methods for agents data access.

    Args:
        config (Config): configuration to use.
        client (HttpClient): HTTP client instance to use for requests
    """

    def __init__(self, config: Config, client: HttpClient):
        self._config = config
        self._http_client = client

    def upload_csv(self, *, filepath: str):
        """Uploads a list of agents to the server."""
        result = self._http_client.post(
            "/agents/csv", files={"file": ("csv_filename", open(filepath, "rb"), "text/csv")}
        )
        return {"created": result["created"]}

    def get_groups(self):
        """Gets a list of agent groups"""
        return self._http_client.get("/agent-groups")

    def get_agents(self):
        """Gets a list of agents"""
        return self._http_client.get("/agents")

    def create_group(self, obj_in):
        """Creates a new agent group"""
        return self._http_client.post("/agent-groups", json=obj_in)

    def update_group(self, pk, obj_in):
        """Updates existing agent group"""
        return self._http_client.put(f"/agent-groups/{pk}", json=obj_in)

    def get_agent(self, group_id):
        """Gets specific agent from group_id"""
        return self._http_client.get(f"/agents?group_id={group_id}")

    def create_agent(self, obj_in):
        """Creates a new agent"""
        return self._http_client.post("/agents", json=obj_in)

    def update_agent(self, pk, obj_in):
        """Updates existing agent"""
        return self._http_client.put(f"/agents/{pk}", json=obj_in)

    def delete_agent(self, pk):
        """Deletes specific agent"""
        return self._http_client.delete(f"/agents/{pk}")

    def match_sessions(self):
        """Calling match-sessions function"""
        return self._http_client.post("/agents/match-sessions")

    def get_experience_weights(self):
        """Gets agents experience weights"""
        return self._http_client.get("/agents/experience-weights")

    def upload_experience_weights(self, *, data: List[Dict] = None, filepath: str = None):
        """Uploads agents experience weights to the server."""
        if not data and not filepath:
            raise ValueError("Either data or filepath must be given.")

        if data:
            return self._http_client.post(
                "/agents/experience-weights/json",
                files={"file": ("agent.json", io.StringIO(json.dumps(data)), "application/json")},
            )
        if not Path(filepath).exists():
            raise ValueError(f"File {filepath} does not exist.")

        with open(filepath, "rb") as f:
            return self._http_client.post(
                "/agents/experience-weights/json",
                files={"file": ("agent.json", f, "application/json")},
            )
