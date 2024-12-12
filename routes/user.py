from flask import request

from middlewares.auth import auth_middleware
from exceptions.exception_handler import exception_handler


def init(app, database):

    @app.route("/api/user/history", methods=["GET"])
    @auth_middleware
    def get_history():
        try:
            user_id = request.user["user_id"]

            cursor = database.cursor()
            cursor.execute(
                """
                SELECT category_id, name, url, created_at FROM history
                WHERE user_id = '%s'
                ORDER BY created_at DESC
                """
                % user_id
            )
            result = cursor.fetchall()

            columns = tuple(desc[0] for desc in cursor.description)
            history = [dict(zip(columns, row)) for row in result]

            return history, 200
        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)
        finally:
            if "cursor" in locals():
                cursor.close()
