import typing as t
from urllib.parse import urljoin, urlparse

import requests


class ClientMixin:
    """A mixin for making requests to the Harness API."""

    BASE_URL: str
    """The base URL for the API to request. Used to resolve relative paths."""

    session: requests.Session
    """A requests session to use for making requests."""

    def _request(
        self,
        method: t.Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        parse_json: bool = True,
        **kwargs,
    ) -> t.Any:
        """Make a request to the Harness API.

        Args:
            method (str): The HTTP method to use.
            path (str): The path to request.
            **kwargs: Additional keyword arguments to pass to the request.

        Raises:
            requests.HTTPError: If the request fails.

        Returns:
            t.Any: The JSON response.
        """
        if not urlparse(path).scheme:
            path = urljoin(self.BASE_URL, path)
        response = getattr(self.session, method.lower())(path, **kwargs)
        response.raise_for_status()
        if parse_json:
            return response.json()
        return response

    def get(self, path: str, **kwargs) -> t.Any:
        """Make a GET request to the Harness API.

        Args:
            path (str): The path to request.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            t.Any: The JSON response.
        """
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> t.Any:
        """Make a POST request to the Harness API.

        Args:
            path (str): The path to request.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            t.Any: The JSON response.
        """
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> t.Any:
        """Make a PUT request to the Harness API.

        Args:
            path (str): The path to request.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            t.Any: The JSON response.
        """
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> t.Any:
        """Make a DELETE request to the Harness API.

        Args:
            path (str): The path to request.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            t.Any: The JSON response.
        """
        return self._request("DELETE", path, **kwargs)
