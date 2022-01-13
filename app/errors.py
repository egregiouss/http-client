import socket


class APIError(Exception):
    arg: str


class ParsingError(APIError):
    def __init__(self, url: str):
        self.arg = url

    def __str__(self):
        return f"Неудалось получить {self.arg}"


class HeaderFormatError(APIError):
    def __init__(self, header: str):
        self.arg = header

    def __str__(self):
        return f"Некорректный формат заголовка: '{self.arg}'"


class ConnectingError(APIError, socket.gaierror):
    def __init__(self, host: str, port):
        self.arg = f"{host}. Порт: {port}"

    def __str__(self):
        return f"Не удалось подключиться по заданному адресу: {self.arg}"

class DecodingError (APIError, socket.gaierror):
    def __init__(self, charset, data):
        self.arg = f"{charset}"
        self.data = data

    def __str__(self):
        return f"Не удалось декодировать {self.data} используя кодировку{self.arg}"

class RedirectionsError(APIError, socket.gaierror):
    def __init__(self, redirections):
        self.arg = f"{redirections}"

    def __str__(self):
        return f"Превышено число перенаправлений. Максимально возможное кол-во: {self.arg}"