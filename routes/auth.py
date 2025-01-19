from flask import request, make_response

from services.auth import auth_service
from middlewares.auth import auth_middleware
from exceptions.exception_handler import exception_handler
from exceptions.api_error import ApiError
from utils.form_validators import (
    LoginValidator,
    RegisterValidator,
    UserConfirmationValidator
)


def init(app, database):

    @app.route("/api/auth/register", methods=["POST"])
    def register():
        try:
            email = request.json["email"]
            password = request.json["password"]

            register_form = RegisterValidator(database=database)
            register_form.validate()
            if register_form.errors:
                raise ApiError.bad_request(errors=register_form.errors)

            auth_service.register(email, password, database)

            return {
                "message": "Пользователь успешно зарегестрирован!",
            }, 201
        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        try:
            email = request.json["email"]
            password = request.json["password"]

            login_form = LoginValidator()
            login_form.validate()
            if login_form.errors:
                raise ApiError.bad_request(errors=login_form.errors)

            refresh_token, data = auth_service.login(email, password, database)

            res = make_response(
                {
                    **data,
                    "message": "Успешная авторизация!",
                }
            )
            res.set_cookie(
                "refresh_token",
                refresh_token,
                httponly=True,
                secure=True,
            )

            return res
        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)

    @app.route("/api/auth/user_confirmation", methods=["POST"])
    @auth_middleware
    def user_confirmation():
        try:
            user_id = request.user["user_id"]
            password = request.json["password"]

            confirmation_form = UserConfirmationValidator()
            confirmation_form.validate()
            if confirmation_form.errors:
                raise ApiError.bad_request(errors=confirmation_form.errors)

            data = auth_service.user_confirmation(user_id, password, database)

            return {
                **data,
                "message": "Успешная идентификация!",
            }, 200
        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)

    @app.route("/api/auth/logout", methods=["POST"])
    def logout():
        try:
            refresh_token = request.cookies.get("refresh_token")

            auth_service.logout(refresh_token, database)

            res = make_response()
            res.set_cookie("refresh_token", "", expires=0)

            return res
        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)

    @app.route("/api/auth/refresh", methods=["POST"])
    def refresh():
        try:
            token = request.cookies.get("refresh_token")
            access_token, refresh_token = auth_service.refresh(token, database)

            res = make_response({"token": access_token})
            res.set_cookie(
                "refresh_token",
                refresh_token,
                httponly=True,
                secure=True,
            )

            return res
        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)
