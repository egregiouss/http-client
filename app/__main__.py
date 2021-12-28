import argparse

from app.client import Client

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("url", type=str, help="URL сервера ддя подключения")
    parser.add_argument("-M", "--method", type=str, choices=["GET", "POST"], default="GET",
                        help="Метод http запроса к серверу")
    parser.add_argument(
        "-H",
        "--headers",
        type=str,
        nargs=2,
        action="append",
        default=[],
        help="Изменить или добавить заголовок. Формат: <header> <value>",
    )
    parser.add_argument("-d", "--data", default="", help="Данные для передачи на сервeр методом POST")
    parser.add_argument("-t", "--timeout", type=str, help="Время ожидания ответа")
    parser.add_argument("-F", "--file", type=str, help="Сохранить данные ответа в файл")
    parser.add_argument("-c", "--cookie", type=str, default="", help="Добавить cookie")

    return parser.parse_args()


def main():

    args = parse_args()


    client = Client(args.url,
                    args.method,
                    args.headers,
                    args.cookie,
                    args.file,
                    args.data,
                    args.timeout,
                    )
    response = client.send_request(client.request)
    client.print_response()


if __name__ == '__main__':
    main()
