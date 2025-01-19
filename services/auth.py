import datetime as dt

import bcrypt

from exceptions.api_error import ApiError
from model.model import ai_model
from services.token import access_token_service, refresh_token_service


class _AuthService:

    def register(self, email, password, database):
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        )

        with database.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (
                    email,
                    password,
                    created_at)
                VALUES (%s, %s, %s)
                """,
                (
                    email,
                    hashed_password.decode("utf-8"),
                    dt.datetime.now(dt.timezone.utc),
                ),
            )
            database.commit()

        return

    def login(self, email, password, database):
        with database.cursor() as cursor:
            cursor.execute(
                """
                SELECT id,
                    email,
                    password
                FROM users
                WHERE email = %s
                """,
                (email,),
            )
            user = cursor.fetchone()

        if (not user) or (
            not bcrypt.checkpw(
                password.encode("utf-8"),
                user[2].encode("utf-8"),
            )
        ):
            raise ApiError.bad_request("Неверный логин или пароль!")

        access_token, refresh_token = self.generate_auth_tokens(
            {
                "user_id": user[0],
                "email": email,
            }
        )

        refresh_token_service.save_token(
            user[0],
            refresh_token,
            None,
            database,
        )

        return (
            refresh_token,
            {
                "token": access_token,
                "categories": ai_model.get_label_config(),
            },
        )

    def user_confirmation(self, user_id, password, database):
        with database.cursor() as cursor:
            cursor.execute(
                """
                SELECT password
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )
            user = cursor.fetchone()

        if not user:
            raise ApiError.unauthorized_error()

        if not bcrypt.checkpw(
            password.encode("utf-8"),
            user[0].encode("utf-8"),
        ):
            raise ApiError.bad_request("Неверный пароль!")

        return {
            "categories": ai_model.get_label_config(),
        }

    def logout(self, refresh_token, database):
        return refresh_token_service.delete_token(refresh_token, database)

    def refresh(self, refresh_token, database):
        if not refresh_token:
            raise ApiError.unauthorized_error()

        data = refresh_token_service.validate_token(refresh_token)
        if not data:
            raise ApiError.unauthorized_error()

        token_db = refresh_token_service.find_token(refresh_token, database)
        if not token_db:
            raise ApiError.unauthorized_error()

        user_id = data["user_id"]
        with database.cursor() as cursor:
            cursor.execute(
                """
                SELECT email
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )
            user = cursor.fetchone()

        tokens = self.generate_auth_tokens(
            {
                "user_id": user_id,
                "email": user[0],
            }
        )
        refresh_token_service.save_token(
            user_id,
            tokens[1],
            refresh_token,
            database,
        )

        return tokens

    def generate_auth_tokens(self, payload):
        access_token = access_token_service.generate_token(payload)
        refresh_token = refresh_token_service.generate_token(payload)

        return access_token, refresh_token


auth_service = _AuthService()
