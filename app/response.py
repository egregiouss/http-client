import re
from dataclasses import dataclass, field


class Response:
    body: str = ''
    charset: str = ''
    code: int = -1
    location: str = None
    headers = {}
    protocol: float = 1.0

    def convert_to_http_format(self):
        response = [f"HTTP/{self.protocol} {self.code} OK"]
        for header, value in self.headers.items():
            response.append(f"{header}: {value}")
        return '\r\n'.join(response).encode()

    def parse(self, data: bytes):
        response = data.decode("utf-8")
        self.code = (re.search(r" [\d]* ", response)).group(0)
        self.protocol = (re.search(r"[\d.]* ", response)).group(0)

        head = response.split("\r\n\r\n")[0]
        self.body = "".join(response.split("\r\n\r\n")[1:])
        self.charset = "utf-8"
        self.content_len = None
        self.headers = {}
        self.location = ""
        for i in head.split("\r\n"):
            search_headers = re.search(r"(?P<header>[a-zA-Z-]*): "
                                       r"" r"(?P<value>[0-9\s\w,.;=/:-]*)", i)
            if search_headers is not None:
                self.headers[search_headers.group("header")] = \
                    search_headers.group("value")
                if (search_headers.group("header") == "Content-Type" or
                        search_headers.group("header") == "content-type"):
                    search_charset = re.search(r"[a-zA-z/]*; " r"charset="
                                               r"(?P<charset>" r"[\w\d-]*)",
                                               search_headers.group("value"))
                    self.charset = 'utf-8' if search_charset is None \
                        else search_charset.group("charset")
                if search_headers.group("header") == "Location" \
                        or search_headers.group("header") == "location":
                    self.location = search_headers.group("value")
                if search_headers.group("header") == "Content-Length" \
                        or search_headers.group("header") == "content-length":
                    self.content_len = search_headers.group("value")
        return self
