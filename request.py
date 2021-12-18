class HTTPRequest:
    def __init__(self,
                 url,
                 method,
                 headers,
                 cookie,
                 timeout):
        self.method = method
        self.url = url
        self.headers = headers
        self.cookie = cookie
        self.timeout = timeout


def build_request(args) -> HTTPRequest:
    pass

