# -*- coding: utf-8 -*-

from txlib.http.base import BaseRequest


class HttpRequest(BaseRequest):
    """Basic http requests handler.

    This class can handle both http and https requests. However, since
    it uses the `requests` module (which in turn uses `urllib2`), it does
    not verify the SSL certificate in case of https.
    """

    def get(self, path):
        """Make a GET request.

        Args:
            `path`: The path to the resource.
        Returns:
            The content of the response.
        Raises:
            An exception depending on the HTTP status code of the response.
        """
        return self._make_request('GET', path)

    def post(self, path, data, filename=None):
        """Make a POST request.

        If a `filename` is not specified, then the data must already be
        JSON-encoded. We specify the Content-Type accordingly.

        Else, we make a multipart/form-encoded request. In this case, the data
        variable must be a dict-like object. The file must already be
        suitably (usually UTF-8) encoded.

        Args:
            `path`: The path to the resource.
            `data`: The data to send. The data must already be JSON-encoded.
            `filename`: The filename of the file to send.
        Returns:
            The content of the response.
        Raises:
            An exception depending on the HTTP status code of the response.
        """
        return self._send('POST', path, data, filename)

    def put(self, path, data, filename=None):
        """Make a PUT request.

        If a `filename` is not specified, then the data must already be
        JSON-encoded. We specify the Content-Type accordingly.

        Else, we make a multipart/form-encoded request. In this case, the data
        variable must be a dict-like object. The file must already be
        suitably (usually UTF-8) encoded.

        Args:
            `path`: The path to the resource.
            `data`: The data to send. The data must already be JSON-encoded.
            `filename`: The filename of the file to send.
        Returns:
            The content of the response.
        Raises:
            An exception depending on the HTTP status code of the response.
        """
        return self._send('PUT', path, data, filename)

    def delete(self, path):
        """Make a DELETE request.

        Args:
            `path`: The path to the resource.
        Returns:
            The content of the response.
        Raises:
            An exception depending on the HTTP status code of the response.
        """
        return self._make_request('DELETE', path)

    def _make_request(self, method, path, data=None, **kwargs):
        """Make a request.

        Use the `requests` module to actually perform the request.

        Args:
            `method`: The method to use.
            `path`: The path to the resource.
            `data`: Any data to send (for POST and PUT requests).
            `kwargs`: Other parameters for `requests`.
        Returns:
            The content of the response.
        Raises:
            An exception depending on the HTTP status code of the response.
        """
        url = self._construct_full_url(path)
        self._auth_info.populate_request_data(kwargs)
        res = requests.request(method, url, data=data, **kwargs)
        if res.code in self.success:
            return res.content
        else:
            raise self._exception_for(res.code)(
                http_code=res.code, msg=res.content
            )

    def _send(self, method, path, data, filename):
        """Send data to a remote server, either with a POST or a PUT request.

        Args:
            `method`: The method (POST or PUT) to use.
            `path`: The path to the resource.
            `data`: The data to send.
            `filename`: The filename of the file to send (if any).
        Returns:
            The content of the response.
        Raises:
            An exception depending on the HTTP status code of the response.
        """
        if filename is None:
            return self._send_json(method, path, data)
        else:
            return self._send_file(method, path, data, filename)

    def _send_json(self, method, path, data):
        """Make a application/json request.

        Args:
            `method`: The method of the request (POST or PUT).
            `path`: The path to the resource.
            `data`: The JSON-encoded data.
        Returns:
            The content of the response.
        Raises:
            An exception depending on the HTTP status code of the response.
        """
        headers = {'Content-type': 'application/json'}
        return self._make_request(method, path, data=data, headers=headers)

    def _send_file(self, method, path, data, filename):
        """Make a multipart/form-encoded request.

        Args:
            `method`: The method of the request (POST or PUT).
            `path`: The path to the resource.
            `data`: The JSON-encoded data.
            `filename`: The filename of the file to send.
        Returns:
            The content of the response.
        Raises:
            An exception depending on the HTTP status code of the response.
        """
        with open(filename, 'r') as f:
            return self._make_request(method, path, data=data, files=[f, ])
