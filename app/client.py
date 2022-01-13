import logging
import socket
import sys
import app.parser as parser
from app.request import Request
from app.response import Response
import re
from app.errors import *

cookies = {}

logger = logging.getLogger(__name__)


def parse_uri(uri):
    _path = '/'
    _scheme = ''

    if re.match('http://', uri):
        uri = uri[7:]
        _scheme = 'http'
    elif re.match(r'https://', uri):
        uri = uri[8:]
        _scheme = 'https'

    _host = uri.split('/')[0]
    if '/' in uri:
        _path += uri[len(_host) + 1:]
    return _host, _path, _scheme


def send(args):
    args = parser.convert_to_list(args)
    _host, _path, scheme = parse_uri(args[0])
    del args[0]
    _request = Request(_host, _path, scheme, *args)
    _request.set_cookies(cookies)
    try:
        _sock = _request.send_data()
    except socket.gaierror:
        logger.info('bad request')
        raise socket.gaierror
    return _sock, _host, _path, scheme


def get(_sock, _host, args):
    _response = Response(_sock, args.file)
    _response.receive(args.file, args.streaming, args.verbose)

    return _response


def change_url(addr, host, scheme):
    if host in addr:
        return addr
    else:
        return scheme + '://' + host + addr


def main():
    try:
        arguments = parser.parse_args()
        sock, host, path, scheme = send(arguments)
        print(sock, host, path, scheme )
        response = get(sock, host, arguments)
        while re.search(r'3\d\d', response.headers['code'].decode()) and arguments.redirects:
            try:
                addr = response.headers['location'][:-2]
                try:
                    arguments.uri = change_url(addr, host, scheme)
                    sock, host, path, scheme = send(arguments)

                except ValueError:
                    continue
                response = get(sock, host, arguments)

            except KeyError:
                logger.info('theres no address to go')
        if not arguments.streaming:
            response.print()

    except KeyboardInterrupt:
        logger.info('closing connections')
        logger.info('client closed')
        sys.exit()



