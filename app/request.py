import re

from yarl import URL
from urllib.parse import urlparse, urljoin, SplitResult, urlunparse
from app.errors import *

def header_key_is_correct(header_key) -> bool:
    if re.search(r"[a-zA-z\-]+", header_key):
        return True
    raise HeaderFormatError(header_key)


class HTTPRequest:
    def __init__(self,
                 url,
                 method,
                 headers,
                 data,
                 cookie=b""):
        self.method = method


        self.url = urlparse(url)
        self.path = self.url.path if self.url.path !='' else '/'
        if not self.url:
            raise UrlParsingError(url)
        self.scheme = self.url.scheme
        self.cookie = cookie
        self.body = data
        self.content_type = "text/plain"

        self.content_length = len(self.body)
        self.headers = self.setup_headers(headers)

    def setup_headers(self, headers: list, ):
        headers_dict = {"Host": self.url.hostname, "Connection": "close","Content-Length": self.content_length}
        if self.method == "POST":
            headers_dict["Content-Length"] = self.content_length


        if self.cookie:
            headers_dict["Cookie"] = self.cookie

        for header in headers:
            if header_key_is_correct(header[0]):
                headers_dict[header[0]] = header[1]

        return headers_dict

    def convert_to_raw(self):
        request = [f"{self.method} {self.path} {'HTTP/1.1'}".encode()]
        for header, value in self.headers.items():
            request.append(f"{header}: {value}".encode())

        request.append(b"")
        request.append(bytes(self.body.encode()))
        return b"\r\n".join(request)

    def change_url(self, url: str, host) -> None:
        if host in url:
            self.url = urlparse(url)
        else:

            self.url = urlparse(urlunparse(self.url)+url)


        self.headers["Host"] = self.url.hostname
        self.scheme = self.url.scheme
        self.path = self.url.path
