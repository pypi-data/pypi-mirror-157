from .custom_error import CustomError, ExceptionMessage
from typing import List, TypedDict

class ValidationDict(TypedDict):
    msg: str
    param: str
class RequestValidationError(CustomError):
    status_code: int = 400
    errors: List[ValidationDict]

    def __init__(self, errors: List[ValidationDict]) -> None:
        self.errors = errors
        super().__init__('Invalid Request Parameters')
    
    def serialize_errors(self) -> List[ExceptionMessage]:
        return list(map(lambda error: {"message": error["msg"] , "field": error["param"] }, self.errors))
        