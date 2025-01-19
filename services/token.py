import datetime as dt
import os

import jwt


class _TokenService:

    def __init__(self, secret_key, exp_params):
        self.__secret_key = secret_key
        self.__exp = dt.timedelta(**exp_params)

    def generate_token(self, payload):
        issued_at = dt.datetime.now(tz=dt.timezone.utc)
        token = jwt.encode(
            payload={
                **payload,
                "exp": issued_at + self.__exp,
                "iat": issued_at,
                "nbf": issued_at,
            },
            key=self.__secret_key,
        )

        return token

    def validate_token(self, token):
        try:
            data = jwt.decode(
                jwt=token,
                key=self.__secret_key,
                algorithms=["HS256"],
            )

            return data
        except:
            return None


class _RefreshTokenService(_TokenService):

    def delete_token(self, token, database):
        with database.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM tokens
                WHERE refresh_token = %s
                """,
                (token,),
            )

            database.commit()

    def find_token(self, token, database):
        with database.cursor() as cursor:
            cursor.execute(
                """
                SELECT refresh_token
                FROM tokens
                WHERE refresh_token = %s
                """,
                (token,),
            )
            return cursor.fetchone()

    def save_token(self, user_id, new_token, old_token, database):
        token_data = old_token and self.find_token(old_token, database)

        with database.cursor() as cursor:
            if token_data:
                cursor.execute(
                    """
                    UPDATE tokens
                    SET refresh_token = %s
                    WHERE refresh_token = %s
                    """,
                    (
                        new_token,
                        token_data,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO tokens (
                        user_id,
                        refresh_token)
                    VALUES (%s, %s)
                    """,
                    (
                        user_id,
                        new_token,
                    ),
                )

            database.commit()


access_token_service = _TokenService(
    os.getenv("JWT_ACCESS_SECRET_KEY"),
    {"minutes": 30},
)

refresh_token_service = _RefreshTokenService(
    os.getenv("JWT_REFRESH_SECRET_KEY"),
    {"days": 30},
)
