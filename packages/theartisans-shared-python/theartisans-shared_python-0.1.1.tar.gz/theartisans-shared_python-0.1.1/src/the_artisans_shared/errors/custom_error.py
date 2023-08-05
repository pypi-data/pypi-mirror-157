from abc import ABC, abstractproperty
from typing import List, TypedDict, Optional

class ExceptionMessage(TypedDict):
    message: str
    field: Optional[str]

class CustomError(ABC, Exception):
    def status_code() -> int: pass
    def message()-> str: pass 

    def __init__(self, message:str) -> None:
        self.message = message
        super().__init__(message)
    
    @abstractproperty
    def serialize_errors(self) -> List[ExceptionMessage]:
        pass