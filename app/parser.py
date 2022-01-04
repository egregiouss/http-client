import argparse
import logging
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('uri',
                        help='URL',
                        type=str)
    parser.add_argument('--method', '-M',
                        help='метод запроса'
                             '{GET|PUT|POST|HEAD|OPTIONS|DELETE}',
                        default='GET')
    parser.add_argument('--body', '-b',
                        help='тело запроса',
                        nargs='*')
    parser.add_argument('--headers', '-H',
                        help='Заголовок запроса в кавычках',
                        nargs='*')
    parser.add_argument('--timeout', '-t',
                        help='таймаут ожидания ответа',
                        type=float,
                        default=10)
    parser.add_argument('--redirects', '-r',
                        help='разрешить перенаправления',
                        action="store_true")
    parser.add_argument('--streaming', '-s',
                        help='выводить данные в консоль по мере получения',
                        action="store_true")
    parser.add_argument('--long', '-l',
                        help='выводить тело ответа',
                        action="store_true")
    parser.add_argument('--verbose', '-v',
                        help='выводить заголовки ответа',
                        action="store_false", default=True)

    parser.add_argument("-f", "--file", type=str, help="Сохранить данные ответа в файл")
    return parser.parse_args()


def convert_to_list(namespace):
    return [
        namespace.uri,
        namespace.method,
        parse_content(namespace.headers),
        '\r\n'.join(parse_content(namespace.body)),
        namespace.timeout
    ]


def parse_content(content):
    if not content:
        return []
    elif len(content) == 1:
        return [content[0][1:-1]]
    _content = []
    _part = None
    try:
        for part in content:
            if part.endswith('"') and part[-2] != '/':
                _part += ' ' + part
                _part = delete_slashes(_part)
                _content.append(_part[1:-1])
            elif part.startswith('"'):
                _part = part
            else:
                _part += ' ' + part
    except ValueError:
        logger.info('something wrong with content')
    return _content


def delete_slashes(string):
    shielding = ['\'', '/"']
    for char in shielding:
        if char == '\'':
            string = string.replace(char, "'")
        else:
            string = string.replace(char, '"')
    return string
