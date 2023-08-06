import logging
from typing import List, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter, Retry, RetryError

from .assets import ASSET_PATHS, EXPORTED_FIELDS, QlikAsset
from .constants import (
    API_BASE_PATH,
    RETRY_BACKOFF_FACTOR,
    RETRY_COUNTS,
    RETRY_STATUSES,
)

logger = logging.getLogger(__name__)


def _session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=RETRY_COUNTS,
        backoff_factor=RETRY_BACKOFF_FACTOR,
        status_forcelist=RETRY_STATUSES,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session


def _check_next_page_url(links: dict, current_page_url: str) -> Optional[str]:
    next_page = links.get("next")
    if not next_page:
        return None

    next_page_url = next_page["href"]
    if next_page_url == current_page_url:
        return None

    return next_page_url


class RestApiClient:
    """
    Client class to connect to Qlik REST API and retrieve Qlik assets

    API documentation: https://qlik.dev/apis/#rest
    """

    def __init__(self, server_url: str, api_key: str):
        self._server_url = server_url
        self._api_key = api_key
        self._session = _session()
        self._authenticate()

    def _authenticate(self):
        auth_header = {"Authorization": "Bearer " + self._api_key}
        self._session.headers.update(auth_header)

    @property
    def server_url(self) -> str:
        """Returns attribute server url"""
        return self._server_url

    def _url(self, asset_path: str) -> str:
        path = API_BASE_PATH + asset_path
        return urljoin(self._server_url, path)

    def _call(self, url: str) -> Optional[dict]:
        try:
            response = self._session.get(url)
            return response.json()
        except RetryError as error:
            logger.warning(error)
            return None

    def _pager(self, first_page_url: str) -> List[dict]:
        current_page_url = first_page_url

        data: List[dict] = []
        while current_page_url:
            response = self._call(current_page_url)
            if not response:
                return data
            data.extend(response["data"])

            next_page_url = _check_next_page_url(
                response["links"], current_page_url
            )
            if not next_page_url:
                return data

            current_page_url = next_page_url
        return data

    def _get(self, asset: QlikAsset) -> List[dict]:
        asset_path = ASSET_PATHS[asset]
        url = self._url(asset_path)
        data = self._pager(url)

        def _filter_fields(row: dict) -> dict:
            return {key: row.get(key) for key in EXPORTED_FIELDS[asset]}

        return [_filter_fields(row) for row in data]

    def spaces(self) -> List[dict]:
        """
        Returns the list of Spaces

        doc: https://qlik.dev/apis/rest/spaces/#%23%2Fentries%2Fspaces-get
        """
        return self._get(QlikAsset.SPACES)

    def users(self) -> List[dict]:
        """
        Returns the list of Users

        doc: https://qlik.dev/apis/rest/users/#%23%2Fentries%2Fusers-get
        """
        return self._get(QlikAsset.USERS)

    def apps(self) -> List[dict]:
        """
        Returns the list of Apps

        doc: https://qlik.dev/apis/rest/items/#%23%2Fentries%2Fitems-get
        """
        return self._get(QlikAsset.APPS)
