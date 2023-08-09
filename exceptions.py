class MessageNotSend(Exception):
    """Сообщение не было доставлено."""

    pass


class InvalidHttpStatus(Exception):
    """Статус HTTP-кода не равен 200."""

    pass


class InvalidRequest(Exception):
    """Ошибка получения request."""

    pass


class UnknownStatus(Exception):
    """Неизвестный статус домашней работы."""

    pass
