from datetime import date, datetime
from typing import List, Literal, Optional, TypedDict, Union

from enderturing import Config
from enderturing.api.api_utils import _to_date_range, _to_time_range
from enderturing.api.schemas import SearchResponse
from enderturing.http_client import HttpClient


SessionsList = TypedDict(
    "SessionsList",
    {
        "total": int,
        "items": List[dict],
    },
)


class Sessions:
    def __init__(self, config: Config, client: HttpClient):
        """
        Args:
            config (Config): configuration to use.
            client (HttpClient): HTTP client instance to use for requests
        """
        self._config = config
        self._http_client = client

    def get_session(self, session_id: str) -> dict:
        """
        Retrieve meta information for particular session (call, chat, email).
        No transcripts will be returned.

        Args:
            session_id: identifier of session (call, chat, email).

        Returns:
            A dictionary containing meta data regarding requested session_id.
        """
        return self._http_client.get(f"/sessions/{session_id}")

    def list(
        self,
        *,
        skip: int = 0,
        max_results: int = 50,
        order_by: str = None,
        from_date: Union[str, date] = None,
        to_date: Union[str, date] = None,
        from_time: str = None,
        to_time: str = None,
        date_label: str = None,
        language: str = None,
        search_query: str = None,
        include_unprocessed: bool = None,
        agents: List[int] = None,
        type: str = None,
    ) -> SessionsList:
        """
        Retrieve meta information for list of sessions (call, chat, email).
        No transcripts will be returned.

        Args:
            skip: skip first N results, for pagination purpose
            max_results: limit maximum number of sessions in result, for pagination purpose
            order_by: possible values: "newest", "oldest", "longest", "longest_silence",
                "most_emotions", "most_overlapped"

            from_date: return session which starts after "2021-11-09"
            to_date: return session which starts prior to "2021-11-09" (from_date value required)
            from_time: filter by start time, applies to each day (each day from 12:00)
            to_time: filter by end time, applies to each day (each day till 18:00)
            date_label: return sessions from specific time range.
                Possible values: "today", "yesterday", "current_week", "last_week",
                "current_month", "last_month"

            search_query: return only sessions with provided phone number
                or agent/sales representative login (caller_id or destination_id)
            language: return only sessions with provided language (ISO 639-1 format)

            include_unprocessed: return unprocessed sessions (by default is False)
            agents: list of agent ids
            type: return only specific type of sessions (possible values: "call", "chat", "email")

        Returns:
            A dictionary with list of items containing sessions and metadata.
        """
        if any((from_date, to_date)) and not all((from_date, to_date)):
            raise ValueError("from_date and to_date always go together")

        params = {
            "date_range": _to_date_range(from_date, to_date),
            "time_range": _to_time_range(from_time, to_time),
            "date_label": date_label,
            "search_query": search_query,
            "language": language,
            "skip": skip,
            "limit": max_results,
            "order_by": order_by,
            "include_unprocessed": include_unprocessed,
            "agents": ",".join(map(str, agents)) if agents else None,
        }
        return self._http_client.get("/sessions", params=params)

    def update(self, session_id: str, session_data: dict):
        """Updates existing session"""
        return self._http_client.put(f"/sessions/{session_id}", json=session_data)

    def search(
        self,
        search_query: str = "",
        skip: int = 0,
        limit: Optional[int] = 10,
        from_date: Optional[Union[str, date, datetime]] = None,
        to_date: Optional[Union[str, date, datetime]] = None,
        language: Optional[str] = None,
        call_duration: Optional[int] = None,
        call_duration_compare: Optional[Literal["gt", "gte", "lt", "lte"]] = "gte",
        silence_percent: Optional[int] = None,
        silence_percent_compare: Optional[Literal["gt", "gte", "lt", "lte"]] = "gte",
    ) -> SearchResponse:
        """Performs search by sessions.

        Args:
            search_query: Search query to for full-text search. By default majority of words
                are expected to be in session transcript.
                You can use quotes to enforce some words or phrases in exact form.
                Sample query:
                  have a good day
                It can match with "have a bad day" text,
                since the majority of query words are in the text.
                Another example query (quoted):
                  "have a good day"
                Would match only with a text containing the entire phrase.
                You can mix quoted and unquoted parts to get what you want.
                Also you can have multiple
                quoted parts of a query. E.g.:
                  have a good day "credit card" "pin"
            skip: Number of sessions to skip, used for pagination
            limit: Number of sessions to return
            from_date: Filter sessions by session.start_dt >= date_from
            to_date: Filter sessions by session.start_dt <= date_to
            language: Filter sessions by language
            call_duration: Filter sessions by duration in seconds. Condition is defined by
            `call_duration_compare` param
            call_duration_compare: Defines how to filter by `call_duration`.
                E.g. if the value is "gt" - only sessions that are longer than `call_duration`
                would be returned
                Supported values:
                    "gt" - greater than.
                    "gte" - greater or equal
                    "lt" - less than
                    "lte" - less or equal
            silence_percent: Filters sessions by percentage of silence. Allowed values 0-100
                Condition is defined by `silence_percent_compare`
            silence_percent_compare: Defines how to filter by `silence_percent`.
                E.g. if the value is "gt" - only session's
                session.silence_percent > silence_percent would be returned.
                Supported values:
                    "gt" - greater than.
                    "gte" - greater or equal
                    "lt" - less than
                    "lte" - less or equal

        Returns:
            Number of matched sessions and requested range of them
        """
        params = {
            "search_query": search_query,
            "skip": skip,
            "limit": limit,
            "date_range": _to_date_range(from_date, to_date),
            "language": language,
            "call_duration": call_duration,
            "call_duration_compare": call_duration_compare,
            "silence_percent": silence_percent,
            "silence_percent_compare": silence_percent_compare,
        }
        return SearchResponse(**self._http_client.get("/sessions/discovery", params=params))

    def get_filter_tags(self, **kwargs):
        """
        **kwargs: dict
            types: Optional[str] = ""
            date_range: str = ""
            date_label: Optional[str]
            time_range: Optional[str]
            language: str = ""
            search_query: str = ""
            destination_id: str = ""
            direction: str = ""
            events_call_id: str = ""
            tags: str = None
            tags_logical_operator: str
            topics: str = None
            duration: str = None
            silence: str = None
            emotions: str = None
            agents: str = None
            include_unprocessed: bool = False
        """
        return self._http_client.get("/sessions/filter/tags", params=kwargs)

    def get_filter_topics(self, **kwargs):
        """
        **kwargs: dict
            types: Optional[str] = ""
            date_range: str = ""
            date_label: Optional[str]
            time_range: Optional[str]
            language: str = ""
            search_query: str = ""
            destination_id: str = ""
            direction: str = ""
            events_call_id: str = ""
            tags: str = None
            tags_logical_operator: str
            topics: str = None
            duration: str = None
            silence: str = None
            emotions: str = None
            agents: str = None
            include_unprocessed: bool = False
        """
        return self._http_client.get("/sessions/filter/topics", params=kwargs)

    def get_filter_choices(self, **kwargs):
        """
        **kwargs: dict
            types: Optional[str] = ""
            date_range: str = ""
            date_label: Optional[str]
            time_range: Optional[str]
            language: str = ""
            search_query: str = ""
            destination_id: str = ""
            direction: str = ""
            events_call_id: str = ""
            tags: str = None
            tags_logical_operator: str
            topics: str = None
            duration: str = None
            silence: str = None
            emotions: str = None
            agents: str = None
            include_unprocessed: bool = False
        """
        return self._http_client.get("/sessions/filter/choices", params=kwargs)

    def get_filter_statistics(self, **kwargs):
        """
        **kwargs: dict
            types: Optional[str] = ""
            date_range: str = ""
            date_label: Optional[str]
            time_range: Optional[str]
            language: str = ""
            search_query: str = ""
            destination_id: str = ""
            direction: str = ""
            events_call_id: str = ""
            tags: str = None
            tags_logical_operator: str
            topics: str = None
            duration: str = None
            silence: str = None
            emotions: str = None
            agents: str = None
            include_unprocessed: bool = False
        """
        return self._http_client.get("/sessions/filter/statistics", params=kwargs)

    def get_transcripts(self, session_id):
        """Retrieve transcripts"""
        return self._http_client.get(f"/sessions/{session_id}/transcripts")

    def chat_upload(self, obj_in):
        return self._http_client.post("/sessions/chats", json=obj_in)
