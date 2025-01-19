import re

from model.model import ai_model


class _ModelService:

    __CACHE_EXP = 604800

    def predict_category(self, url, text, redis_cache,):
        processed_url = re.sub(r"[^a-zA-Z0-9]", "", url)
        redis_key = f"predictions:{processed_url}"
        if redis_cache.exists(redis_key):
            category_id = int(redis_cache.get(redis_key))
        else:
            preprocessed_text = ai_model.preprocess_text(text)
            category_id = ai_model.predict(preprocessed_text)
            redis_cache.setex(redis_key, self.__CACHE_EXP, category_id)

        return category_id


model_service = _ModelService()
