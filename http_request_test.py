import unittest
from unittest import mock, TestCase
import app.parser as parser
import app.client as HTTP_client
from app.request import Request
from app.response import Response
import io


def get_fake_socket(text=b'', to=15):
    sock = mock.Mock()
    sock.makefile.return_value = io.BytesIO(text)
    sock.sendall.return_value = None
    sock.settimeout.return_value = to
    sock.connect.return_value = None
    sock.close.return_value = None
    return sock


def get_fake_reader(text=b''):
    return io.BytesIO(text)


class TestArguments(TestCase):
    def check_args(self, args, host=None):
        if host:
            _host, _ = HTTP_client.parse_uri(args[0])
            self.assertEqual(_host, host)
        testing_req = Request(None, None, 'https', *args[1:])
        self.assertEqual(testing_req.method, args[1])
        self.assertEqual(testing_req.headers, args[2])
        self.assertEqual(testing_req.body, args[3])



    def test_correct_args(self):
        args = [
            ['example.org'],
            'GET',
            'Content-type: text/html',
            'some body'
        ]
        self.check_args(args)

    def test_correct_args_two(self):
        args = [
            ['www.cyberforum.ru/python-network/thread1911394.html'],
            'GET',
            ['header 1', 'header2', 'header3'],
            'another sample of body'
        ]
        self.check_args(args)


class MockResponse:
    def __init__(self):
        self.sock = None
        self.response_headers = None
        self.response_body = None
        self.response_body_len = 0
        self.headers = None
        self.cookies = None
        self.filename = None
        self.ext = None
        self.charset = None
        self.connection = True

        self.response = Response(get_fake_socket(b''), 'test')

    def _set_text_to_sock(self, text, to=15):
        self.response.sock = get_fake_socket(text, to)

    def _get_reader(self, text):
        self._set_text_to_sock(text)
        return self.response.sock.makefile()

    def _set_body(self, text):
        self.response.response_body = text

    def receive_headers(self, text):
        reader = self._get_reader(text)
        self.response.get_headers(reader)
        self.response.headers['code'] = self.response.headers['code'].decode()

        self.headers = self.response.headers
        self.response_headers = self.response.response_headers
        self.cookies = self.response.cookies


    def static_recv(self, text, length):
        reader = self._get_reader(text)
        self.response.static_recv(reader, length, False, False)

        self.response_body = self.response.response_body

    def dynamic_recv(self, text):
        reader = self._get_reader(text)
        self.response.dynamic_recv(reader, False, False)

        self.response_body = self.response.response_body
        self.response_body_len = self.response.response_body_len

    def receive(self):
        self.response.receive(False, False)

        self.headers = self.response.headers
        self.response_headers = self.response.response_headers
        self.cookies = self.response.cookies
        self.response_body = self.response.response_body
        self.charset = self.response.charset


class TestFunctionalityResponse(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response = Response(get_fake_socket(b''), '')

    def clear_response(self):
        self.response.response_headers = ''
        self.response.response_body = b''

        self.response.headers = {}  # i.e. 'Content-Type: text/html'
        self.response.cookies = []  # cookie pairs

        self.response.filename = None
        self.response.ext = 'html'
        self.response.charset = None
        self.response.connection = True

    def test_receive_headers(self):
        text = b'HTTP-code\r\nHeader: value\r\n\r\n'
        response = MockResponse()
        response.receive_headers(text)

        self.assertEqual(response.headers,
                         {
                             'code': 'HTTP-code\r\n',
                             'header': 'value\r\n'
                         })
        self.assertEqual(response.response_headers,
                         'Header: value\r\n')

    def test_getting_cookie(self):
        text = b'code\r\nSet-Cookie: cookie\r\n\r\n'
        response = MockResponse()
        response.receive_headers(text)

        self.assertEqual(response.cookies, ['cookie\r\n'])

    def test_getting_multiple_cookies(self):
        text = b'code\r\nSet-Cookie: cookie1\r\nSet-Cookie: cookie2\r\n\r\n'
        response = MockResponse()
        response.receive_headers(text)

        self.assertEqual(response.cookies, ['cookie1\r\n', 'cookie2\r\n'])



    def test_static_recv(self):
        text = b'abrakadabra'
        response = MockResponse()
        response.static_recv(text, len(text))

        self.assertEqual(response.response_body, text)
        self.clear_response()


    def test_full_receive_with_handled_headers(self):
        text = b'HTTP 200 OK\r\nHeader: value\r\nContent-Type: text/html; ' \
               b'charset=utf8\r\nContent-Length: 14\r\nConnection: close' \
               b'\r\n\r\nsome body text'
        self.response.sock = get_fake_socket(text)

        self.response.receive(False, True, True)

        self.assertEqual(self.response.charset, 'utf8\r\n')
        self.assertEqual(self.response.connection, False)
        print(self.response.response_body)
        self.assertEqual(self.response.response_body_len, 11)



class MockRequest:
    def __init__(self):
        self.host = None
        self.path = None
        self.method = None
        self.headers = None
        self.body = None
        self.timeout = None
        self.request = None

    def _create_request(self, host='www.example.com', path='/', method='GET',
                        headers=None, body='', to=15):
        if headers is None:
            headers = []

        self.request = Request(host, path, "https", method, headers, body, to)

    def form_message(self):
        result = self.request.convert_to_http()

        self.headers = self.request.headers
        return result

    def modify_data(self):
        self.request.modify_data()

        self.body = self.request.body
        self.headers = self.request.headers

    def send_data(self, sockets):
        with mock.patch('socket.socket', get_fake_socket):
            return self.request.send_data(sockets)

    def set_cookies(self, cookies):
        self.request.set_cookies(cookies)

        self.headers = self.request.headers


class TestFunctionalityRequest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = None



    def test_forming_messages_with_headers(self):
        request = MockRequest()
        request._create_request(headers=['Header: value',
                                         'Another-Header: value'],
                                body='somebody')

        expect = b'GET / HTTP/1.1\r\nHost: www.example.com\r\nHeader: value' \
                 b'\r\nAnother-Header: value\r\n'
        actual = request.form_message()

        self.assertEqual(expect, actual)

    def test_modifying_data_with_body(self):
        headers = ['Access-Encoding: gzip', 'Content-Type: plain/text; '
                                            'charset=utf8']
        body = 'texttextexttexttext'

        request = MockRequest()
        request._create_request(headers=headers,
                                body=body)

        request.modify_data()

        self.assertEqual(request.headers, [
            'Access-Encoding: gzip',
            'Content-Type: plain/text; charset=utf8',
            f'Content-Length: {len(body)}\r\n'
        ])

    def test_modifying_data_with_no_body(self):
        headers = ['Access-Encoding: gzip', 'Content-Type: plain/text; '
                                            'charset=utf8']
        request = MockRequest()
        request._create_request(headers=headers)

        request.modify_data()

        self.assertEqual(request.headers, [
            'Access-Encoding: gzip',
            'Content-Type: plain/text; charset=utf8\r\n',
        ])


if __name__ == '__main__':
    unittest.main()