import datetime as dt

from psycopg2.extras import RealDictCursor


class _UserService:

    __ITEMS_ON_PAGE = 10

    def get_history(self, user_id, page, database):
        with database.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                    SELECT category_id,
                        name,
                        url,
                        created_at
                    FROM history
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    OFFSET %s
                    """,
                (user_id, self.__ITEMS_ON_PAGE, self.__ITEMS_ON_PAGE * page),
            )
            history = cursor.fetchall()

            cursor.execute(
                """
                    SELECT COUNT(*)
                    FROM history
                    WHERE user_id = %s
                    """,
                (user_id,),
            )
            total_count = cursor.fetchone()["count"]

            return {
                "total_count": total_count,
                "items_on_page": self.__ITEMS_ON_PAGE,
                "history": history,
            }

    def add_to_history(self, user_id, category_id, name, url, database):
        with database.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO history (
                        user_id,
                        category_id,
                        name,
                        url,
                        created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                (
                    user_id,
                    category_id,
                    name[:100],
                    url,
                    dt.datetime.now(dt.timezone.utc).strftime(
                        r"%Y-%m-%d %H:%M:%S",
                    ),
                ),
            )
            database.commit()


user_service = _UserService()
