import os
import json


def get_labels_id():
    with open(
        f"{os.path.dirname(os.path.abspath(__file__))}/model_bundle/label_to_id.json",
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)["categories_id"]
    return {int(key): data[key] for key in data}


def get_neutral_category_id():
    with open(
        f"{os.path.dirname(os.path.abspath(__file__))}/model_bundle/label_to_id.json",
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)["neutral_category"]
