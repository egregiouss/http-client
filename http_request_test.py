import unittest

import pytest

from app.request import HTTPRequest
from app.client import Client
from app.errors import DecodingError

def test_do_request():
    http_client = Client('https://vk.com', 'GET', [], None, None, "", 2)
    response = http_client.send_request(http_client.request)
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

def test_sch9():
    http_client = Client('https://sch9.ru/news', 'GET',
                         [],
                         None, None, "", 2)

    response = http_client.send_request(http_client.request)




def test_big():
    http_client = Client('https://raw.githubusercontent.com/dwyl/english-words/master/words.txt', 'GET',
                         [],
                         None, None, "", 2, False, True)
    resp = http_client.send_request(http_client.request)
    assert int(resp.content_len) == len(resp.body)

def test_yandex():
    http_client = Client('https://ulearn.me', 'GET',
                         [],
                         None, None, "", 2)
    try:
        resp = http_client.send_request(http_client.request)
    except DecodingError as e:
        pytest.fail(str(e))



if __name__ == '__main__':
    unittest.main()
