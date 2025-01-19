from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import (
    InputRequired,
    Length,
    EqualTo,
    Email,
    ValidationError,
    StopValidation,
)
from exceptions.exception_handler import exception_handler


class LoginValidator(FlaskForm):
    email = StringField(
        "email",
        validators=[
            InputRequired("Обязательное поле"),
            Email(message="Некорректная почта"),
        ],
    )
    password = StringField(
        "password",
        validators=[
            InputRequired("Обязательное поле"),
        ],
    )


class RegisterValidator(FlaskForm):
    email = StringField(
        "email",
        validators=[
            InputRequired("Обязательное поле"),
            Email(message="Некорректная почта"),
        ],
    )
    password = StringField(
        "password",
        validators=[
            InputRequired("Обязательное поле"),
            Length(
                min=6,
                message="Пароль должен быть минимум из 6 символов",
            ),
        ],
    )
    password_confirm = StringField(
        "password_confirm",
        validators=[
            InputRequired("Обязательное поле"),
            EqualTo("password", "Пароли не совпадают"),
        ],
    )

    def __init__(self, *args, database=None, **kwargs):
        super(RegisterValidator, self).__init__(*args, **kwargs)
        self.database = database

    def validate_email(self, email):
        if email.errors:
            raise StopValidation()

        try:
            with self.database.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT email
                    FROM users
                    WHERE email = %s
                    """,
                    (email.data,),
                )
                user = cursor.fetchone()
            if user:
                raise ValidationError("Почта уже используется")

        except Exception as ex:
            if isinstance(ex, (ValidationError, StopValidation)):
                raise ex
            return exception_handler(ex)


class UserConfirmationValidator(FlaskForm):
    password = StringField(
        "password",
        validators=[
            InputRequired("Обязательное поле"),
        ],
    )
