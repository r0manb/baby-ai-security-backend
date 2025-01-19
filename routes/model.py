from flask import request

from services.model import model_service
from services.user import user_service
from model.model import ai_model
from exceptions.exception_handler import exception_handler
from middlewares.auth import auth_middleware


def init(app, database, redis_cache):

    @app.route("/api/predict", methods=["POST"])
    @auth_middleware
    def predict():
        try:
            user_id = request.user["user_id"]
            name = request.json["name"]
            url = request.json["url"]
            text = request.json["text"]

            category_id = model_service.predict_category(
                url,
                text,
                redis_cache,
            )
            if category_id != ai_model.get_neutral_category_id():
                user_service.add_to_history(
                    user_id,
                    category_id,
                    name,
                    url,
                    database,
                )

            return {"category_id": category_id}, 200
        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)
