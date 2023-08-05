from typing import Any
from flask import Flask
from werkzeug.wrappers import Request
import base64, json

class NodeCookieSessionDecode:
    def __init__(self, app:Flask):
        self.app = app
    
    def __call__(self, environ, start_response, *args: Any, **kwargs: Any) -> Any:
        request = Request(environ)
        try:
            session_cookie = request.cookies.get('session')
            session = json.loads(base64.b64decode(session_cookie)) or {}
            environ['session'] = session
        except:
            pass
        return self.app(environ, start_response)
