from functools import wraps, partial
from typing import Callable
from flask import request
from the_artisans_shared.errors import RequestValidationError
from marshmallow import ValidationError

    
def request_valiator(f: Callable, body_schema_class=None, query_schema_class=None, param_schema_class=None):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if body_schema_class is not None:
                body_data = request.get_json()
                body_schema_class().load(data = body_data)
            if query_schema_class is not None:
                query_data = request.args.to_dict()
                print(query_data)
                query_schema_class().load(data = query_data)
            if param_schema_class is not None:
                param_data = request.view_args
                param_schema_class().load(data = param_data)
        except ValidationError as e:
            errors = [{ "param": value, "msg": e.messages[value][0]} for key, value in enumerate(e.messages) ]
            raise RequestValidationError(errors=errors)
        return f(*args, **kwargs)
    return decorated_function

def validate_request (body_schema_class=None, query_schema_class=None, param_schema_class=None):
    return partial(request_valiator, body_schema_class=body_schema_class, query_schema_class=query_schema_class, param_schema_class=param_schema_class)