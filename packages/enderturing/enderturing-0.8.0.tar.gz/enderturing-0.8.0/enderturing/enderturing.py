import logging

from typing import Optional

from enderturing.api import (
    Agent,
    Asr,
    Connectors,
    Filters,
    Hashtags,
    Playlists,
    Raw,
    Reports,
    Scorecard,
    Services,
    Sessions,
    System,
    Tags,
    Topics,
    Trainings,
    Triggers,
    Users,
)
from enderturing.config import AsrConfig, Config
from enderturing.http_client import HttpClient
from enderturing.speech_recognizer import SpeechRecognizer


log = logging.getLogger("enderturing")


class EnderTuring:
    """Object to access Ender Turing API.

    Attributes:
        asr (Asr): Group of methods to access/modify configuration of ASR instances
        sessions (Sessions): Group of methods to access/modify sessions
        raw (Raw): Group of methods to access/modify raw transcripts and events
        agent (Agent): Group of methods to access/modify agents
        hashtags (Hashtags): Group of methods to access/modify hashtags
        tags (Tags): Group of methods to access/modify tags
        topics (Topics): Group of methods to access/modify topics
        filters (Filters): Group of methods to access/modify filters
        reports (Reports): Group of methods to access/modify reports
        connectors (Connectors): Group of methods to access/modify connectors
        playlists (Playlists): Group of methods to access/modify playlists
        services (Services): Group of methods to access/modify services
        system (System): Group of methods to access/modify system
        trainings (Trainings): Group of methods to access/modify trainings
        triggers (Triggers): Group of methods to access/modify triggers
        users (Users): Group of methods to access/modify users
    """

    def __init__(self, config: Config = None):
        self._config = config or Config.from_env()

        self.http_client = HttpClient(self._config)

        self.agent = Agent(self._config, self.http_client)
        self.asr = Asr(self._config, self.http_client)
        self.connectors = Connectors(self._config, self.http_client)
        self.filters = Filters(self._config, self.http_client)
        self.hashtags = Hashtags(self._config, self.http_client)
        self.playlists = Playlists(self._config, self.http_client)
        self.raw = Raw(self._config, self.http_client)
        self.reports = Reports(self._config, self.http_client)
        self.scorecards = Scorecard(self._config, self.http_client)
        self.services = Services(self._config, self.http_client)
        self.sessions = Sessions(self._config, self.http_client)
        self.system = System(self._config, self.http_client)
        self.tags = Tags(self._config, self.http_client)
        self.topics = Topics(self._config, self.http_client)
        self.trainings = Trainings(self._config, self.http_client)
        self.triggers = Triggers(self._config, self.http_client)
        self.users = Users(self._config, self.http_client)

    def get_speech_recognizer(
        self, *, asr_instance: Optional[dict] = None, language: Optional[str] = None
    ):
        """Creates a `SpeechRecognizer`.
        If called without parameters - tries to initialize recognizer from environment variables.

        Args:
            asr_instance: ASR instance details, returned by API. Used to set recognizer config.
            language: Language to get speech recognizer for. If there is no instances configured for
                the specified language - `ValueError` is raised.

        Returns:
            Initialized `SpeechRecognizer` instance.

        Raises:
            ValueError: if both `language` and `asr_instance`
            are set or no active ASR instance find for the language.
        """
        if language and asr_instance:
            raise ValueError("Parameters `asr_instance` and `language` are mutually exclusive")
        if language:
            instances = self.asr.get_instances(active_only=True, languages=[language])
            if not instances:
                raise ValueError(f"No active ASR instances found for language '{language}'")
            if len(instances) > 1:
                log.warning(
                    "More than one instance found for language '%s'"
                    " using the first one (name: '%s')",
                    language,
                    instances[0]["name"],
                )
            asr_config = AsrConfig(
                url=instances[0]["ws_url"],
                sample_rate=instances[0]["sample_rate"],
                language=language,
            )
        elif asr_instance:
            asr_config = AsrConfig(
                url=asr_instance["ws_url"], sample_rate=asr_instance["sample_rate"]
            )
        else:
            asr_config = AsrConfig.from_env()

        return SpeechRecognizer(asr_config, api_config=self._config)
