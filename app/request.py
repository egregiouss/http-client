import re

from yarl import URL


def header_key_is_correct(header_key) -> bool:
    if re.search(r"[a-zA-z\-]+", header_key):
        return True
    raise ValueError("Incorrect header name!")


class HTTPRequest:
    def __init__(self,
                 url,
                 method,
                 headers,
                 data,
                 cookie=b""):
        self.method = method
        self.scheme = "https"
        self.url = URL(url)
        self.cookie = cookie
        self.body = data
        self.content_type = "text/plain"

        self.content_length = len(self.body)
        self.headers = self.setup_headers(headers)

    def setup_headers(self, headers: list, ):
        headers_dict = {"Host": URL(self.url).host, "Connection": "close","Content-Length": self.content_length}
        if self.method == "POST":
            headers_dict["Content-Length"] = self.content_length


        if self.cookie:
            headers_dict["Cookie"] = self.cookie

        for header in headers:
            if header_key_is_correct(header[0]):
                headers_dict[header[0]] = header[1]
        return headers_dict

    def convert_to_raw(self):
        request = [f"{self.method} {self.url.raw_path_qs} {'HTTP/1.1'}".encode()]
        for header, value in self.headers.items():
            request.append(f"{header}: {value}".encode())
        print(request)
        print(type(self.body))
        request.append(b"")
        request.append(bytes(self.body.encode()))
        print(request)
        return b"\r\n".join(request)

    def change_url(self, url: str) -> None:
        self.url = URL(url)
        self.headers["Host"] = URL(url).host
        self.scheme = URL(url).scheme
        self.path = URL(url).path
