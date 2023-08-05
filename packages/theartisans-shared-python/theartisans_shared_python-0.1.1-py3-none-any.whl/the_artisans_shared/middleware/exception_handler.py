from flask import jsonify
from the_artisans_shared.errors import CustomError

def exception_handler(e: Exception):
    if isinstance(e, CustomError):
        return jsonify({ "errors": e.serialize_errors()}), e.status_code
    print(e)
    return jsonify({"errors": [{"message": "Something went wrong"}]}), 400