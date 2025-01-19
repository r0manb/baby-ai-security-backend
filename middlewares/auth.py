from functools import wraps

from flask import request

from exceptions.exception_handler import exception_handler
from exceptions.api_error import ApiError
from services.token import access_token_service


def auth_middleware(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            if not request.authorization:
                return exception_handler(ApiError.unauthorized_error())

            token = str(request.authorization).split()[1]
            token_data = access_token_service.validate_token(token)
            if not token_data:
                return exception_handler(ApiError.unauthorized_error())

            request.user = {
                "user_id": token_data["user_id"],
                "email": token_data["email"],
            }

            return func(*args, **kwargs)

        except:
            return exception_handler(ApiError.unauthorized_error())

    return decorated_function
