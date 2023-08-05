import os
from typing import Dict, Union

import fasttext
import wget
from kolibri.settings import DATA_PATH

models = {"low_mem": None, "high_mem": None}


target_path=os.path.join(DATA_PATH, 'modules', 'language_detector', 'lid.176.bin')
module_path=os.path.join(DATA_PATH, 'modules', 'language_detector')

def download_model(name):
    url = f"https://dl.fbaipublicfiles.com/fasttext/supervised-models/{name}"
#    target_path = os.path.join(FTLANG_CACHE, name)
    if not os.path.exists(target_path):
        os.makedirs(module_path, exist_ok=True)
        wget.download(url=url, out=module_path)
    return target_path


def get_or_load_model(low_memory=False):
    if low_memory:
        model = models.get("low_mem", None)
        if not model:
            model_path = download_model("lid.176.ftz")
            model = fasttext.load_model(model_path)
            models["low_mem"] = model
        return model
    else:
        model = models.get("high_mem", None)
        if not model:
            model_path = download_model("lid.176.bin")
            model = fasttext.load_model(model_path)
            models["high_mem"] = model
        return model


def detect_language(text: str,  num_languages=2, use_large_model=True) -> Dict[str, Union[str, float]]:
    model = get_or_load_model(not use_large_model)
    labels, scores = model.predict(text.replace('\r', '').replace('\n', ''), k=num_languages)
    predictions=zip(labels, scores)
    predictions = {k.replace("__label__", ''): v for k, v in predictions}

#    score = min(float(scores[0]), 1.0)
    return predictions

print(detect_language("Zentraler Rechnungseingang Ihre Nachricht wurde dem Postfach 'Zentraler Rechnungseingang' zugestellt.\r\nYour mail message was sent to 'Zentraler Rechnungseingang'"))
