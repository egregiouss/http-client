import argparse
from app.request import build_request

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("url", type=str, help="URL сервера ддя подключения")
    parser.add_argument("-m", "--method", type=str, choices=["GET", "POST"], default="GET",
                        help="Метод http запроса к серверу")
    parser.add_argument(
        "-H",
        "--headers",
        type=str,
        nargs="+",
        help="add headers in request")
    parser.add_argument("-d", "--data", type=str, help="Данные для передачи на сервeр методом POST")
    parser.add_argument("-t", "--timeout", type=str, help="Время ожидания ответа")
    parser.add_argument("-O", "--output", type=str, help="Сохранить данные ответа в файл")
    parser.add_argument("-c", "--cookie", type=str, help="Добавить cookie")

    return parser.parse_args()


def main():
    args = parse_args()
    request = build_request(args)


if __name__ == 'main':
    main()
