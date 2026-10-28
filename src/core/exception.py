import sys
from src.core.logger import logger


def error_message_detail(error: Exception, error_detail: sys) -> str:

    _, _, exc_tb = error_detail.exc_info()

    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    error_message = f"Error occurred in python script: [{file_name}] at line number [{line_number}]: {str(error)}"

    logger.error(
        "Exception raised",
        file=file_name,
        line=line_number,
        error=str(error),
    )

    return error_message


class MyException(Exception):
    def __init__(self, error_message: str, error_detail: sys):
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_detail)

    def __str__(self) -> str:
        """
        Returns the string representation of the error message.
        """
        return self.error_message





    