import socket
import ssl
import sys
import time
from enum import Enum

from yarl import URL

from app.request import HTTPRequest
from app.response import Response

class OutputType(Enum):
    File = 1,
    Console = 2

class Client():
    def __init__(self, url, method, headers,  cookie, file, body=b"", timeout=2):
        print(url, method, headers,  cookie, file, body, timeout)
        print(type(body))
        self.file = file
        self.method = method
        self.headers = headers
        self.cookie = cookie
        self.body = body
        self.request = self.build_request(url, method, headers, body, cookie)
        print(self.request)
        self.sock = self.setup_socket(timeout, self.request.scheme)



    def build_request(self, url, method, headers, body, cookie) -> HTTPRequest:
        request = HTTPRequest(url, method, headers, body, cookie)

        return request

    def setup_socket(self, timeout, scheme):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if scheme == "https":
            s = ssl.wrap_socket(s)
        s.settimeout(timeout)
        return s

    def send_request(self, timeout: int = 1000,
                   max_iterations: int = 10) :
        while max_iterations >= 0:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.request.scheme == "https":
                sock = ssl.wrap_socket(sock)
            sock.settimeout(timeout)
            max_iterations -= 1
            addr = (self.request.url.host,
                          80 if self.request.scheme == 'http' else 443)
            sock.connect(addr)
            if self.request.url.scheme == "https":
                sock.do_handshake()

            sock.sendall(self.request.convert_to_raw())
            obtained_data = b''
            while True:
                data = sock.recv(1024)
                if not data:
                    break
                obtained_data += data
            sock.close()
            response = Response().parse(obtained_data)
            if 300 <= int(response.code) < 400:
                self.request.change_url(response.location)
            else:
                self.response = response
                return self.response

    def print_response(self):
        answer = [f'{self.response.convert_to_http_format().decode()}', '\r\n', self.response.body]
        if self.file:
            with open(self.file, 'bw') as file:
                file.write(self.response.body.encode(self.response.charset))
        else:
            sys.stdout.write("\r\n".join(answer))