from typing import List, Optional

from enderturing import Config
from enderturing.http_client import HttpClient


class Asr:
    def __init__(self, config: Config, client: HttpClient):
        """
        Args:
            config (Config): configuration to use.
            client (HttpClient): HTTP client instance to use for requests
        """
        self._config = config
        self._http_client = client

    def _is_asr_up(self, asr_data):
        return (
            asr_data
            and "containers_status" in asr_data
            and asr_data["containers_status"]
            and all((x["running"] > 0 for x in asr_data["containers_status"]))
        )

    def get_instances(self, active_only: bool = True, languages: Optional[List[str]] = None):
        result = self._http_client.get("/asr")
        if active_only:
            result = (x for x in result if self._is_asr_up(x))
        if languages:
            result = (x for x in result if x["language"] in languages)
        return list(result)

    def create_instance(self, obj_in):
        """Creates a new ASR"""
        return self._http_client.post("/asr", json=obj_in)

    def get_status(self):
        """Returns status of all instances"""
        return self._http_client.get("/asr/status")

    def get_languages(self):
        """Retrieve languages list. Only active (already downloaded images) languages must be shown.
        Used for ASR views"""
        return self._http_client.get("/asr/languages")

    def get_instance(self, pk):
        """Gets a single instance"""
        return self._http_client.get(f"/asr/{pk}")

    def update_instance(self, pk, obj_in):
        """Updates an instance by id"""
        return self._http_client.put(f"/asr/{pk}", json=obj_in)

    def delete_instance(self, pk):
        """Deletes an instance"""
        return self._http_client.delete(f"/asr/{pk}")

    def get_instance_status(self, pk):
        """Gets a status of the instance"""
        return self._http_client.get(f"/asr/{pk}")

    def start_container(self, pk, docker_service):
        """Starts a docker container"""
        return self._http_client.post(f"/asr/{pk}/{docker_service}")

    def stop_container(self, pk, docker_service):
        """Stops a docker container"""
        return self._http_client.delete(f"/asr/{pk}/{docker_service}")
