import unittest

from app.request import HTTPRequest
from app.client import Client


def test_do_request():
    http_client = Client('https://vk.com', 'GET', [], None, None, "", 2)
    response = http_client.send_request()
    assert int(response.code) == 200
    assert float(response.protocol) == 1.1


def test_request():
    http_client = Client('https://vk.com', 'GET', [], None, None, "", 2)
    request = http_client.request
    expected_bytes_request: str = 'GET / HTTP/1.1\r\n' \
                                  'Host: vk.com\r\n' \
                                  'Connection: close\r\n' \
                                  'Content-Length: 0\r\n\r\n'
    assert request.convert_to_raw().decode() == expected_bytes_request


def test_set_method_with_url():
    http_client = Client('https://vk.com/feed', 'POST',
                         [['Cookie', 1234], ['Reference', 'blablacar.com'], ['User-Agent', 'Yandex']],
                         None, None, 'Hello', 2)
    request = http_client.request
    expected_bytes_request: str = 'POST /feed HTTP/1.1\r\n' \
                                  'Host: vk.com\r\n' \
                                  'Connection: close\r\n' \
                                  'Content-Length: 5\r\n' \
                                  'Cookie: 1234\r\n' \
                                  'Reference: blablacar.com\r\n' \
                                  'User-Agent: Yandex\r\n\r\n' \
                                  'Hello'
    assert request.convert_to_raw().decode() == expected_bytes_request



if __name__ == '__main__':
    unittest.main()
