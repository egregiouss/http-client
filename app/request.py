import re
import socket
import gzip
import ssl
from datetime import datetime
from  app.errors import *


class Request:
    def __init__(self, host, path, scheme, method, headers, body, to=15):
        self.host = host
        self.path = path
        self.method = method
        self.headers = headers
        self.body = body
        self.timeout = to
        self.scheme = scheme
        self.PORT = 80 if scheme == 'http' else 443

    @property
    def method(self):
        return self.__method

    @method.setter
    def method(self, method):
        if re.match(r'GET|PUT|POST|HEAD|OPTIONS|DELETE', method) is None:
            raise ValueError('incorrect method')
        else:
            self.__method = method

    def send_data(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.PORT))
        except ConnectingError as e:
            raise ConnectingError(self.host, self.PORT)
        sock.settimeout(self.timeout)
        if self.scheme == 'https':
            sock = ssl.wrap_socket(sock)
            sock.do_handshake()
        self.modify_data()

        msg = self.convert_to_http()
        sock.sendall(msg + self.body)
        return sock

    def set_cookies(self, cookies):
        try:
            cookies[self.host]
        except KeyError:
            return

        header = []
        time_parse = ['%a, %d %b %Y %H:%M:%S %Z', '%a, %d-%b-%Y %H:%M:%S %Z',
                      '&a %b %d %H:%M:%S %Y']

        for cookie in cookies[self.host]:
            pairs = cookie[:-2].split('; ')
            for i in range(len(pairs) - 1, -1, -1):
                pair = pairs[i]
                if i == 0:
                    header.append(pairs[i])

                if re.match(r'[Pp]ath', pair):
                    if not self.path.startswith(pair.split('=')[1]):
                        break
                elif re.match(r'[Ee]xpires', pair):
                    expires_at = None
                    for time in time_parse:
                        try:
                            expires_at = datetime.strptime(pair.split('=')[1],
                                                           time)
                            break
                        except ValueError:
                            continue
                    if not expires_at:
                        print('I\'ve got bad time')

                    if datetime.utcnow() > expires_at:
                        break
        if header:
            self.headers.append(f'Cookie: {"; ".join(header)}')

    def modify_data(self):
        charset = 'utf8'
        compression = None

        if not self.body.endswith('\r\n\r\n') and len(self.body) > 0:
            self.body += '\r\n\r\n'

        for header in self.headers:
            if header.casefold() == 'content-type':
                charset = header.split('=')[1]
            elif header.casefold() == 'accept-encoding':
                compression = header.split(': ')

        self.body = self.body.encode(charset)

        if compression is not None:
            if compression == 'gzip':
                gzip.compress(self.body)

        if self.body:
            self.headers.append(f'Content-Length: {len(self.body) - 4}\r\n')
        elif len(self.headers) > 0:
            self.headers[-1] += '\r\n'

    def convert_to_http(self):
        self.headers = '\r\n'.join(self.headers)
        message = f'{self.method} {self.path} HTTP/1.1\r\n' \
                  f'Host: {self.host}\r\n' \
                  f'{self.headers}\r\n'
        return bytes(message, encoding='utf8')
