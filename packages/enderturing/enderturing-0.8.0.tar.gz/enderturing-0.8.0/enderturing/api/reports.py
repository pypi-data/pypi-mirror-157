from enum import Enum
from typing import Union

from enderturing import Config
from enderturing.http_client import HttpClient


class FileFormat(str, Enum):
    txt = "txt"
    csv = "csv"
    xlsx = "xlsx"


class Reports:
    """Contains methods for reports.

    Args:
        config (Config): configuration to use.
        client (HttpClient): HTTP client instance to use for requests
    """

    def __init__(self, config: Config, client: HttpClient):
        self._config = config
        self._http_client = client

    def read_subscription(self):
        """Gets a subscription from server"""
        return self._http_client.get("/reports/subscription")

    def create_or_update_subscription(self, obj_in):
        """Creates a new subscription or updates if subscription already exists"""
        return self._http_client.put("/reports/subscription", json=obj_in)

    def send_subscription(self):
        """Sending subscription"""
        return self._http_client.post("/reports/subscription/send")

    def download_report_file(self, file_format: FileFormat, name, **kwargs) -> Union[str, bytes]:
        """
        Args:
            file_format: string 'csv', 'txt' or 'xlsx'
            name: string
            **kwargs: dict
                chart_params: string
                types: string
                date_range: string
                date_label: string
                time_range: string
                language: string
                search_query: string
                destination_id: string
                direction: string
                events_call_id: string
                tags: string
                tags_logical_operator: string
                topics: string
                agents: string
                duration: string
                silence: string
                emotions: string
                include_unprocessed: string 'false' or 'true'
        Returns file content (text or binary)
        """
        return self._http_client.get(
            f"/reports/chart-data/download/{file_format}?name={name}", params=kwargs
        )
