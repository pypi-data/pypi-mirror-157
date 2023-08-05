import logging
from typing import Iterable, Optional, Tuple

from ...utils import (
    OUTPUT_DIR,
    current_timestamp,
    deep_serialize,
    from_env,
    get_output_filename,
    validate_baseurl,
    write_json,
    write_summary,
)
from .assets import QlikAsset
from .client import RestApiClient
from .constants import API_KEY, BASE_URL

logger = logging.getLogger(__name__)


def iterate_all_data(
    client: RestApiClient,
) -> Iterable[Tuple[QlikAsset, list]]:
    """Iterate over the extracted data from Qlik"""

    logger.info("Extracting SPACES from REST API")
    yield QlikAsset.SPACES, deep_serialize(client.spaces())

    logger.info("Extracting USERS from REST API")
    yield QlikAsset.USERS, deep_serialize(client.users())

    logger.info("Extracting APPS from REST API")
    yield QlikAsset.APPS, deep_serialize(client.apps())


def extract_all(
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    output_directory: Optional[str] = None,
) -> None:
    """
    Extract data from Qlik REST API
    Store the output files locally under the given output_directory
    """

    _output_directory = output_directory or from_env(OUTPUT_DIR)
    _base_url = validate_baseurl(base_url or from_env(BASE_URL))
    _api_key = api_key or from_env(API_KEY)
    client = RestApiClient(server_url=_base_url, api_key=_api_key)

    ts = current_timestamp()

    for key, data in iterate_all_data(client):
        filename = get_output_filename(key.name.lower(), _output_directory, ts)
        write_json(filename, data)

    write_summary(_output_directory, ts, base_url=client.server_url)
