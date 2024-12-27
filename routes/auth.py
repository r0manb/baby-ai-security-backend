import datetime

from flask import request
import bcrypt

from middlewares.auth import auth_middleware
from exceptions.exception_handler import exception_handler
from exceptions.exception_handler import ApiError
from utils.Token import Token
from utils.form_validators import (
    create_register_validator,
    create_login_validator,
    create_user_confirmation_validator,
)
from model.label_handler import get_labels_id


def init(app, database):

    @app.route("/api/auth/register", methods=["POST"])
    def register():
        try:
            email, password = request.json["email"], request.json["password"]

            register_form = create_register_validator(database)
            register_form.validate()
            if register_form.errors:
                raise ApiError.bad_request(errors=register_form.errors)

            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            cursor = database.cursor()
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
                    datetime.datetime.now(datetime.timezone.utc),
                ),
            )
            database.commit()

            return {"message": "Пользователь успешно зарегестрирован!"}, 201
        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)
        finally:
            if "cursor" in locals():
                cursor.close()

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        try:
            email, password = request.json["email"], request.json["password"]

            login_form = create_login_validator()
            login_form.validate()
            if login_form.errors:
                raise ApiError.bad_request(errors=login_form.errors)

            cursor = database.cursor()
            cursor.execute(
                """
                SELECT id,
                       email,
                       password
                FROM users
                WHERE email = '%s'
                """
                % email
            )
            user = cursor.fetchone()
            if (not user) or (
                not bcrypt.checkpw(password.encode("utf-8"), user[2].encode("utf-8"))
            ):
                raise ApiError.bad_request("Неверный логин или пароль!")

            token = Token.generate_token({"userId": user[0], "email": user[1]})

            return {
                "token": token,
                "categories": get_labels_id(),
                "message": "Успешная авторизация!",
            }, 200
        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)
        finally:
            if "cursor" in locals():
                cursor.close()

    @app.route("/api/auth/user_confirmation", methods=["POST"])
    @auth_middleware
    def user_confirmation():
        try:
            user_id, password = request.user["user_id"], request.json["password"]

            confirmation_form = create_user_confirmation_validator()
            confirmation_form.validate()
            if confirmation_form.errors:
                raise ApiError.bad_request(errors=confirmation_form.errors)

            cursor = database.cursor()
            cursor.execute(
                """
                SELECT id,
                       password
                FROM users
                WHERE id = '%s'
                """
                % user_id
            )
            user = cursor.fetchone()
            if not user:
                raise ApiError.unauthorized_error()

            if not bcrypt.checkpw(password.encode("utf-8"), user[1].encode("utf-8")):
                raise ApiError.bad_request("Неверный пароль!")

            return {
                "categories": get_labels_id(),
                "message": "Успешная идентификация!",
            }, 200
        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)
        finally:
            if "cursor" in locals():
                cursor.close()
