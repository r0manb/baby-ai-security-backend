import os
import re
import json

import nltk
from nltk.corpus import stopwords
import pymorphy2
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


nltk.download("stopwords")
nltk.download("punkt_tab")


class _Model:

    def __init__(self, model_path, stopwords, morph, label_config_name):
        self.__model_path = model_path
        self.__label_config_path = f"{self.__model_path}/{label_config_name}"

        with open(
            self.__label_config_path,
            "r",
            encoding="utf-8",
        ) as file:
            self.__label_config = json.load(file)

        self.stopwords = stopwords
        self.morph = morph

        self.__tokenizer = AutoTokenizer.from_pretrained(self.__model_path)
        self.__model = AutoModelForSequenceClassification.from_pretrained(
            self.__model_path
        )
        self.__device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu",
        )

        self.__model.eval()
        self.__model.to(self.__device)

    def preprocess_text(self, text):
        text = re.sub(
            r"http\S+|www.\S+|mailto:\S+|[^а-яё\s]",
            "",
            text.lower(),
        )
        tokens = [
            self.morph.normal_forms(token)[0]
            for token in text.split()
            if token not in self.stopwords and token.isalpha()
        ]

        return " ".join(tokens)

    def predict(self, text):
        inputs = self.__tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )
        inputs = {k: v.to(self.__device) for k, v in inputs.items()}

        with torch.no_grad():
            logits = self.__model(**inputs).logits

        predicted_class_id = logits.argmax(dim=-1).item()
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        confidence = probabilities[0, predicted_class_id].item()
        print(predicted_class_id, confidence)
        return predicted_class_id

    def get_label_config(self):
        return self.__label_config

    def get_labels_id(self):
        return self.__label_config["list"]

    def get_neutral_category_id(self):
        return self.__label_config["neutral_category_id"]


ai_model = _Model(
    f"{os.path.dirname(os.path.abspath(__file__))}/model_bundle",
    stopwords.words("russian"),
    pymorphy2.MorphAnalyzer(),
    "label_to_id.json",
)
