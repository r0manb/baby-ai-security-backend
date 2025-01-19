from flask import request

from services.user import user_service
from middlewares.auth import auth_middleware
from exceptions.exception_handler import exception_handler


def init(app, database):
    @app.route("/api/user/history", methods=["GET"])
    @auth_middleware
    def get_history():
        try:
            user_id = request.user["user_id"]
            page = int(request.args.get("page") or 0)

            data = user_service.get_history(user_id, page, database)

            return data, 200
        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)
