from ast import arg


class TelegramException(Exception):
    def __init__(self, *args: object) -> None:
        self.message = 'Telegram unknown error'
        if args:
            self.message = args[0]
            

    def __str__(self) -> str:
        return self.message