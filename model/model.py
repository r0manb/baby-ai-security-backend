import os
import re

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pymorphy2
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

from .label_handler import get_labels_id


nltk.download("stopwords")
nltk.download("punkt_tab")
russian_stopwords = stopwords.words("russian")
morph = pymorphy2.MorphAnalyzer()


def preprocess_text(text):
    text = re.sub(r"http\S+|www.\S+|mailto:\S+|[^а-яё\s]", "", text.lower())
    tokens = [
        morph.normal_forms(token)[0]
        for token in word_tokenize(text, language="russian")
        if token not in russian_stopwords and token.isalpha()
    ]

    return " ".join(tokens)


model_path = os.path.dirname(os.path.abspath(__file__)) + "/model_bundle"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

id_to_label = get_labels_id()


def predict(text):
    inputs = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=512,
        return_tensors="pt",
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs).logits

    predicted_class_id = logits.argmax(dim=-1).item()
    probabilities = torch.nn.functional.softmax(logits, dim=-1)
    confidence = probabilities[0, predicted_class_id].item()
    print(predicted_class_id, id_to_label[predicted_class_id], confidence)
    return predicted_class_id
