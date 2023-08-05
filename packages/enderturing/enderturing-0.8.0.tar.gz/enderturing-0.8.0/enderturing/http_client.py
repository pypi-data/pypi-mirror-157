import datetime
import logging

from typing import Optional, TypedDict, Union

import requests
import urllib3


logger = logging.getLogger("enderturing")


class AuthData(TypedDict):
    token_type: str
    access_token: str
    expires_in: int
    expires_on: datetime.datetime


TOKEN_EXP_TIME_WINDOW = datetime.timedelta(seconds=60)


class HttpClient:
    def __init__(self, config):
        self.config = config
        self._auth_data: Optional[AuthData] = None
        if not config.ssl_verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _get_full_api_url(self, path) -> str:
        return f"{self.config.url.strip('/')}/api/{self.config.api_version}{path}"

    def _get_auth_data(self) -> AuthData:
        if self._auth_data:
            if self._auth_data["expires_on"] - TOKEN_EXP_TIME_WINDOW < datetime.datetime.now():
                logger.info("Token expired, refreshing...")
                self._auth_data = None
            else:
                return self._auth_data

        auth_data = {"username": self.config.auth_key, "password": self.config.auth_secret}
        logger.info("Authenticating to Ender Turing SpeechEngine: %s", self.config.url)
        auth = requests.post(
            self._get_full_api_url("/login/access-token"),
            data=auth_data,
            verify=self.config.ssl_verify,
        )
        auth.raise_for_status()
        authorization_json = auth.json()

        self._auth_data = AuthData(
            token_type=authorization_json["token_type"],
            access_token=authorization_json["access_token"],
            expires_in=int(authorization_json["expires_in"]),
            expires_on=datetime.datetime.now()
            + datetime.timedelta(seconds=int(authorization_json["expires_in"])),
        )

        logger.info(
            "Authenticated, got token: xxxxx%s (expires in: %s seconds)",
            self._auth_data["access_token"][-4:],
            authorization_json["expires_in"],
        )
        return self._auth_data

    def _get_auth_headers(self) -> dict:
        data = self._get_auth_data()
        return {"Authorization": f"{data['token_type']} {data['access_token']}"}

    def get(self, url: str, params: Optional[dict] = None) -> Union[dict, list, str, bytes]:
        """Executes authorized GET requests to API.

        Args:
            url : Target URL, excluding api version prefix (e.g. /events).
            params : Query parameters, which would be serialized as HTTP GET parameters.

        Returns:
            Parsed response JSON, plain text or binary
        """
        response = requests.get(
            self._get_full_api_url(url),
            headers=self._get_auth_headers(),
            params=params,
            verify=self.config.ssl_verify,
        )
        response.raise_for_status()
        if response.headers["content-type"] == "application/json":
            response_json = response.json()
            logger.debug("JSON response for %s: %s", url, str(response_json))
            return response_json
        elif response.headers["content-type"].startswith("text"):
            logger.debug(
                "text response (%s) for %s: %s",
                response.headers["content-type"],
                url,
                response.text,
            )
            return response.text
        else:
            logger.debug(
                "bytes response (%s) for %s: %s...",
                response.headers["content-type"],
                url,
                response.content[:1000],
            )
            return response.content

    def put(self, url: str, json: Union[dict, list] = None, **kwargs) -> Union[dict, list]:
        """Executes authorized PUT requests to API.

        Args:
            url : Target URL, excluding api version prefix (e.g. /events/).
            json : Request body, would be serialized as json.

        Returns:
            Parsed response JSON, can be any type that can be returned by json.loads(),
            but in most cases it's either dict or list.
        """
        response = requests.put(
            self._get_full_api_url(url),
            headers=self._get_auth_headers(),
            json=json,
            verify=self.config.ssl_verify,
            **kwargs,
        )
        response.raise_for_status()
        response_json = response.json()
        logger.debug("JSON response for %s: %s", url, str(response_json))
        return response_json

    def post(self, url: str, json: Union[dict, list] = None, **kwargs) -> dict:
        """Executes authorized POST requests to API.

        Args:
            url : Target URL, excluding api version prefix (e.g. /events).
            json : Request body, would be serialized as json.

        Returns:
            Parsed response JSON, can be any type that can be returned by json.loads(),
            but in most cases it's either dict or list.
        """
        response = requests.post(
            self._get_full_api_url(url),
            headers=self._get_auth_headers(),
            json=json,
            verify=self.config.ssl_verify,
            **kwargs,
        )
        response.raise_for_status()
        response_json = response.json()
        logger.debug("JSON response for %s: %s", url, str(response_json))
        return response_json

    def delete(self, url: str, json: Union[dict, list] = None, **kwargs) -> Union[dict, list]:
        """Executes authorized DELETE requests to API.

        Args:
            url : Target URL, excluding api version prefix (e.g. /events).
            json : Request body, would be serialized as json.

        Returns:
            Empty response
        """
        response = requests.delete(
            self._get_full_api_url(url),
            headers=self._get_auth_headers(),
            json=json,
            verify=self.config.ssl_verify,
            **kwargs,
        )
        response.raise_for_status()
        response_json = response.json()
        logger.debug("JSON response for %s: %s", url, str(response_json))
        return response_json
