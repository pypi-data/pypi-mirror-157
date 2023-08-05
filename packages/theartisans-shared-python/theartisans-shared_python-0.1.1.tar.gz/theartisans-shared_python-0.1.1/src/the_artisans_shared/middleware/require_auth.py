from functools import wraps
from typing import Callable
from flask import request
from the_artisans_shared.errors import NotAuthorizedError

def require_auth(f: Callable):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user') or request.current_user is None:
            raise NotAuthorizedError()
        return f(*args, **kwargs)
    return decorated_function