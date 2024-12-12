import time

from flask import request

from model import model
from exceptions.exception_handler import exception_handler
from middlewares.auth import auth_middleware


def init(app, database):

    @app.route("/api/predict", methods=["POST"])
    @auth_middleware
    def predict():
        try:
            user_id = request.user['user_id']
            name, url = request.json['name'], request.json['url']

            preprocessed_text = model.preprocess_text(request.json["text"])
            category_id, confidence = model.predict(preprocessed_text)

            cursor = database.cursor()
            cursor.execute(
                """
                INSERT INTO history (user_id, category_id, name, url, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, category_id, name[:100], url, round(time.time())),
            )
            database.commit()

            return {
                "category_id": category_id,
                "category_label": "category_label",
                "confidence": confidence,
            }, 200

        except Exception as ex:
            print(repr(ex))
            return exception_handler(ex)
        finally:
            if "cursor" in locals():
                cursor.close()
