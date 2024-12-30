from flask import request
from psycopg2.extras import RealDictCursor

from middlewares.auth import auth_middleware
from exceptions.exception_handler import exception_handler


def init(app, database):

    ITEMS_ON_PAGE = 10

    @app.route("/api/user/history", methods=["GET"])
    @auth_middleware
    def get_history():
        try:
            user_id = request.user["user_id"]
            page = int(request.args.get("page") or 0)
            cursor = database.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT category_id,
                       name,
                       url,
                       created_at
                FROM history
                WHERE user_id = '%s'
                ORDER BY created_at DESC
                LIMIT %s
                OFFSET %s
                """,
                (user_id, ITEMS_ON_PAGE, ITEMS_ON_PAGE * page),
            )
            history = cursor.fetchall()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM history
                WHERE user_id = '%s'
                """
                % user_id
            )
            total_count = cursor.fetchone()['count']

            return {
                "total_count": total_count,
                "items_on_page": ITEMS_ON_PAGE,
                "history": history,
            }, 200
        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)
        finally:
            if "cursor" in locals():
                cursor.close()
