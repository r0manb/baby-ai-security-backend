import sys
import os

from flask import Flask
from flask_cors import CORS
import psycopg2
import redis
from dotenv import load_dotenv

import routes


def main():
    load_dotenv()

    try:
        db_conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        redis_cache = redis.Redis(
            host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0
        )
    except Exception as ex:
        print("Ошибка базы данных:", repr(ex))
        sys.exit()

    app = Flask(__name__)

    CORS(app)
    app.config["WTF_CSRF_ENABLED"] = False

    routes.init(app, db_conn, redis_cache)

    app.run(debug=True)


if __name__ == "__main__":
    main()
