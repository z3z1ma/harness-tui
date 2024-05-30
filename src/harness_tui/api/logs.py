import json
import typing as t

import requests
import sseclient

from harness_tui.api.mixin import ClientMixin
from harness_tui.utils import ttl_cache


class LogClient(ClientMixin):
    BASE_URL = "https://app.harness.io/gateway/log-service/"

    def __init__(
        self,
        session: requests.Session,
        /,
        *,
        account: str,
        org: str,
        project: str,
    ) -> None:
        """A wrapper around the Harness API for managing pipelines.

        Args:
            api_key (str): The Harness API key.
            account (str): The Harness account identifier.
            org (str): The Harness organization identifier.
            project (str): The Harness project identifier.
            session (requests.Session): An authenticated requests session.
        """
        self.session = session
        self.account = account
        self.org = org
        self.project = project

    @ttl_cache(300)
    def get_log_token(self):
        """Get a log token."""
        return self._request(
            "GET", "token", params={"accountID": self.account}, parse_json=False
        ).text

    def blob(self, log_key: str) -> t.Iterable[str]:
        """Get a new line delimited json blob of log data."""
        for line in self._request(
            "GET",
            "blob",
            headers={
                "Accept": "*/*",
                "Content-Type": "application/json",
                "X-Harness-Token": self.get_log_token(),
            },
            params={"accountID": self.account, "X-Harness-Token": "", "key": log_key},
            parse_json=False,
        ).iter_lines():
            yield json.loads(line.decode("utf-8"))

    def stream(self, log_key: str) -> t.Iterable[str]:
        """Stream log data."""
        response = self._request(
            "GET",
            "stream",
            headers={
                "Accept": "*/*",
                "Content-Type": "application/json",
                "X-Harness-Token": self.get_log_token(),
            },
            params={"accountID": self.account, "X-Harness-Token": "", "key": log_key},
            stream=True,
            parse_json=False,
        )
        for sse in sseclient.SSEClient(response).events():  # type: ignore
            if sse.event == "ping":
                continue
            elif sse.event == "error":
                if sse.data.upper() == "EOF":
                    break
                else:
                    raise Exception(f"Error streaming logs: {sse.data}")
            else:
                yield json.loads(sse.data)
