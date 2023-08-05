from .custom_error import CustomError, ExceptionMessage
from typing import List

class NotAuthorizedError(CustomError):
    status_code: int = 401

    def __init__(self) -> None:
        super().__init__('Not Authorized')
    
    def serialize_errors(self) -> List[ExceptionMessage]:
        return [{"message": self.message}] 