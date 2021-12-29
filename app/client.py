import io
import logging
import time

from tqdm import tqdm
import socket
import ssl
import sys
from enum import Enum
from app.request import HTTPRequest
from app.response import Response
from app.errors import *
logger = logging.getLogger(__name__)



class OutputType(Enum):
    File = 1,
    Console = 2

class Client():
    def __init__(self, url, method, headers,  cookie, file, body=b"", timeout=2, verbose=False):
        self.port = None
        self.pbar = None
        self.response = None
        self.head = None
        self.file = file
        self.method = method
        self.headers = headers
        self.cookie = cookie
        self.body = body
        self.request = self.build_request(url, method, headers, body, cookie)
        self.timeout = timeout
        self.verbose = verbose


    def build_request(self, url, method, headers, body, cookie) -> HTTPRequest:
        request = HTTPRequest(url, method, headers, body, cookie)
        return request


    def send_request(self, request,
                   max_iterations: int = 10):
        while max_iterations >= 0:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                if request.scheme == "https":
                    sock = ssl.wrap_socket(sock)
                addr = (self.request.url.hostname,
                            80 if self.request.url.scheme == 'http' else 443)
                self.port = addr[1]
                try:
                    logger.info(f"Attempting to connect to: {self.request.url.hostname}")
                    sock.connect(addr)
                except ConnectionRefusedError as e:
                    raise ConnectingError(request.url.hostname, self.port)


                sock.settimeout(self.timeout)
                max_iterations -= 1
                logger.info("https handshake")
                if request.url.scheme == "https":
                    sock.do_handshake()

                sock.sendall(request.convert_to_raw())
                obtained_data = b''
                obtained_data = self.get_head(obtained_data, sock)
                obtained_data = self.get_body(obtained_data, sock)
                try:
                    self.response = Response().parse(obtained_data)
                except UnicodeDecodeError as e:
                    continue
                if 300 <= int(self.response.code) < 400:

                    self.request.change_url(self.response.location, self.request.url.hostname)
                else:
                    return self.response
        raise RedirectionsError(max_iterations)

    def get_body(self, obtained_data, sock):
        while True:
            data = sock.recv(1024)
            if not data:
                break
            obtained_data += data
            if self.pbar is not None:
                self.pbar.update(1024)

        return obtained_data

    def get_head(self, obtained_data, sock):
        while True:
            data = sock.recv(4)
            if not data:
                break
            obtained_data += data
            if "\r\n\r\n" in obtained_data.decode():
                self.head = Response().parse(obtained_data)
                if self.head.content_len is not None and int(self.head.content_len) != 0 and int(self.head.code) == 200:
                    self.pbar = tqdm(total=int(self.head.content_len) + 1)

                break
        return obtained_data

    def print_head(self, head):
        head: str = head.convert_to_http_format().decode()
        sys.stdout.write(head)

    def print_body_part(self, part):
        sys.stdout.write(part.decode())


    def print_response(self):
        headers = ''
        if self.verbose:
            headers = self.response.convert_to_http_format().decode()
        answer = [f'{headers}', '\r\n', self.response.body]

        if self.file:
           with open(self.file, 'bw') as file:
              file.write(self.response.body.encode(self.response.charset))
        else:
            s = "\r\n".join(answer)
            sys.stdout.write("\r\n".join(answer))
