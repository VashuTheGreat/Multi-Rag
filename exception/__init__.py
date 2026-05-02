import sys
import logging



class MyException(Exception):
    def __init__(self, error_message: str, error_detail: sys):
        super().__init__(error_message)

        logging.exception(error_message)
    def __str__(self) -> str:
        """
        Returns the string representation of the error message.
        """
        return self.args[0]