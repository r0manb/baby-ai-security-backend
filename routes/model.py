import datetime
import re

from flask import request

from model import model
from model.label_handler import get_neutral_category_id
from exceptions.exception_handler import exception_handler
from middlewares.auth import auth_middleware


def init(app, database, redis_cache):

    @app.route("/api/predict", methods=["POST"])
    @auth_middleware
    def predict():
        try:
            user_id = request.user["user_id"]
            name, url = request.json["name"], request.json["url"]

            processed_url = re.sub(r"[^a-zA-Z0-9]", "", url)
            redis_key = f"predictions:{processed_url}"
            if redis_cache.exists(redis_key):
                category_id = int(redis_cache.get(redis_key))
            else:
                preprocessed_text = model.preprocess_text(request.json["text"])
                category_id = model.predict(preprocessed_text)
                redis_cache.setex(redis_key, 604800, category_id)

            if get_neutral_category_id() != category_id:
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
                            datetime.datetime.now(datetime.timezone.utc).strftime(
                                r"%Y-%m-%d %H:%M:%S"
                            ),
                        ),
                    )
                    database.commit()

            return {"category_id": category_id}, 200
        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)
