from .custom_error import CustomError, ExceptionMessage
from typing import List

class NotFoundError(CustomError):
    status_code: int = 404

    def __init__(self) -> None:
        super().__init__('Not Found')
    
    def serialize_errors(self) -> List[ExceptionMessage]:
        return [{"message": self.message}] 