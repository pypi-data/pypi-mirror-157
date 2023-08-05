from .custom_error import CustomError, ExceptionMessage
from typing import List

class BadRequestError(CustomError):
    status_code: int = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
    
    def serialize_errors(self) -> List[ExceptionMessage]:
        return [{"message": self.message}]        