import json
import logging
from typing import Any, Callable, Dict, Optional, Union

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3 import Retry

log = logging.getLogger(__name__)

CONTEXT_HEADER_KEY = "x-spymaster-context"
CONTEXT_ID_HEADER_KEY = "x-spymaster-context-id"

JsonType = Union[str, int, float, bool, list, Dict[str, Any], None]

DEFAULT_RETRY_STRATEGY = Retry(
    raise_on_status=False,
    total=3,
    backoff_factor=0.2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "OPTIONS", "GET", "POST", "PUT", "DELETE"],
)


class BaseHttpClient:
    def __init__(self, base_url: str, retry_strategy: Optional[Retry]):
        self.base_url = base_url
        self.set_retry_strategy(retry_strategy or DEFAULT_RETRY_STRATEGY)

    def set_retry_strategy(self, retry_strategy: Optional[Retry]):
        self.session = requests.Session()
        retry_adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", retry_adapter)
        self.session.mount("https://", retry_adapter)

    def _http_call(self, endpoint: str, method: Callable, parse: bool = True, **kwargs) -> Union[dict, Response]:
        url = f"{self.base_url}/{endpoint}"
        headers = kwargs.pop("headers", None) or {}
        log_context = getattr(log, "context", None)
        if log_context:
            headers[CONTEXT_HEADER_KEY] = json.dumps(log_context)
        response = method(url, headers=headers, **kwargs)
        _log_data(url=url, response=response)
        response.raise_for_status()
        if parse:
            return response.json()
        return response

    def _get(self, endpoint: str, data: dict, **kwargs) -> dict:
        return self._http_call(endpoint=endpoint, method=self.session.get, params=data, **kwargs)  # type: ignore

    def _post(self, endpoint: str, data: dict, **kwargs) -> dict:
        return self._http_call(endpoint=endpoint, method=self.session.post, json=data, **kwargs)  # type: ignore


def _log_data(url: str, response: Response):
    try:
        data = response.json()
    except Exception:  # noqa
        data = response.content
    log.debug(
        f"Got status code {response.status_code}.",
        extra={"status_code": response.status_code, "url": url, "data": data},
    )
