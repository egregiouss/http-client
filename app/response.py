import re
import gzip
from tqdm import tqdm
from app.errors import *




class Response:
    def __init__(self, sock, filename):
        self.sock = sock
        self.response_headers = ''
        self.response_body = b''
        self.response_body_len = 0
        self.headers = {}
        self.cookies = []
        self.filename = filename
        self.charset = None
        self.connection = True
        self.file = None

    def receive(self, is_file, is_streaming, is_verb):
        with self.sock.makefile(mode='rb') as fd:
            self.get_headers(fd)
            if 'content-length' in self.headers.keys():
                content_length = self.headers['content-length']
                self.static_recv(fd, int(content_length), is_file, is_streaming)
            else:
                try:
                    _ = self.headers['transfer-encoding']
                    self.dynamic_recv(fd, is_file, is_streaming)
                except KeyError:
                    raise HeaderFormatError("transfer-encoding")
            if is_verb:
                self.print_headers()

        try:
            encoding = self.headers['accept-encoding']
            if 'gzip' in encoding:
                self.response_body = gzip.decompress(
                    self.response_body)
        except KeyError:
            pass

        try:
            cont_type = self.headers['content-type']
            if re.search(r'charset', cont_type) is not None:
                self.charset = cont_type.split('=')[1]
        except KeyError:
            pass

    def get_headers(self, reader):
        self.headers['code'] = reader.readline()
        header = reader.readline()
        while header != b'\r\n':
            header = header.decode('iso-8859-1')
            self.response_headers += header
            values = header.split(': ')
            key = values[0]
            value = ':'.join(values[1:])
            if key == 'Set-Cookie':
                if 'deleted' not in value:
                    self.cookies.append(value)
            elif key == 'Connection':
                if re.match(r'[Cc]lose', value):
                    self.connection = False
            elif key.lower() == 'content-type':
                try:
                    if re.search(r'charset', value) is not None:
                        self.charset = value.split('=')[1]
                except KeyError:
                    pass
            else:
                self.headers[key.casefold()] = value
            header = reader.readline()

    def print(self):
        if self.charset is not None:
            print(self.response_body.decode(self.charset))
        else:
            print(self.response_body)

    def print_headers(self):
        print(f"\r\n{self.headers['code'].decode('iso-8859-1')}")
        print(self.response_headers)

    def static_recv(self, reader, length, is_file, is_streaming, pbar=None):
        if not pbar:
            pbar = tqdm(total=length)
        count_of_updates = 11
        fragment = length // count_of_updates
        remain = length % count_of_updates
        if is_file and self.file is None:
            self.file = open(self.filename, 'wb')
        for i in range(count_of_updates):
            data = reader.read(fragment)
            self.response_body_len += len(data)
            self.print_chunk(data, is_file, is_streaming)
            pbar.update(fragment)
        end = reader.read(remain)
        self.print_chunk(end, is_file, is_streaming)
        pbar.update(remain)
        if pbar.total == length:
            pbar.close()
            if is_file and self.file is not None:
                self.file.close()

    def print_chunk(self, chunk, is_file, is_streaming):
        if is_file and self.file is not None:
            self.file.write(chunk)
            self.file.flush()
        elif is_streaming:
            print(chunk)
        else:
            self.response_body += chunk

    def dynamic_recv(self, reader, is_file, is_streaming):
        pbar = tqdm(total=65536)
        chunk_size = get_chunk_size(reader)
        while chunk_size != 0:
            if self.response_body_len + chunk_size > pbar.total:
                raising_total = (self.response_body_len + chunk_size) * 2
                pbar.total += raising_total
            self.static_recv(reader, chunk_size, is_file, is_streaming, pbar)
            chunk_size = get_chunk_size(reader)

        pbar.total = self.response_body_len
        pbar.close()

def get_chunk_size(reader):
    hex_chunk_size=''
    try:
        hex_chunk_size = reader.readline()
        if hex_chunk_size == b'\r\n':
            hex_chunk_size += reader.readline()

        print(hex_chunk_size)
        return int(hex_chunk_size.decode('iso-8859-1'), 16)
    except ValueError as e:
        raise DecodingError('iso-8859-1', hex_chunk_size)