import fasttext
import logging
import operator
import os
import requests
import threading
import tqdm
from langid.langid import LanguageIdentifier, model as langid_model
from pycld2 import detect as cld_detect

_langid_model = None
_fasttext_model = None
_init_lock = threading.Lock()


def _download_fasttext():
    remote_url = 'https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin'
    expected_size = 131266198

    model_dir = os.path.expanduser(os.path.join('~', '.nlpclean'))
    os.makedirs(model_dir, exist_ok=True)

    model_name = 'lid.176.bin'
    model_path = os.path.join(model_dir, model_name)

    if os.path.exists(model_path) and os.path.getsize(model_path) == expected_size:
        return model_path

    remote_size = int(requests.head(remote_url).headers['Content-Length'])
    if expected_size != remote_size:
        raise AssertionError('Unexpected remote model size')

    bar = tqdm.tqdm(initial=0, total=remote_size, unit='B', unit_scale=True, desc=model_name)
    req = requests.get(remote_url, stream=True)
    with open(model_path, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                bar.update(1024)
    bar.close()

    return model_path


def detect_main_lang(text, warnings=True):
    global _langid_model
    with _init_lock:
        if _langid_model is None:
            _langid_model = LanguageIdentifier.from_modelstring(langid_model, norm_probs=True)

    global _fasttext_model
    with _init_lock:
        if _fasttext_model is None:
            _fasttext_model = fasttext.load_model(_download_fasttext())

    langs = {}

    cld_best_lang, cld_best_score = False, None
    try:
        _, _, scores = cld_detect(text)
        if len(scores):
            cld_best_lang = scores[0][1]
            cld_best_score = scores[0][2] / 100.
        for _, lang, score, _ in scores:
            if lang not in langs:
                langs[lang] = []
            langs[lang].append(score / 100.)
    except Exception as e:
        if warnings:
            logging.warning(e)

    fst_best_lang, fst_best_score = False, None
    try:
        scores = _fasttext_model.predict(text.replace('\n', ' '), 3)
        if len(scores):
            fst_best_lang = scores[0][0].replace('__label__', '')
            fst_best_score = scores[1][0]
        for lang, score in zip(*scores):
            lang = lang.replace('__label__', '')
            if lang not in langs:
                langs[lang] = []
            langs[lang].append(score)
    except Exception as e:
        if warnings:
            logging.warning(e)

    # Fast path
    if cld_best_lang == fst_best_lang and cld_best_lang and 'un' != cld_best_lang:
        score = (cld_best_score + fst_best_score) / 2.
        sure = score > 0.75
        return cld_best_lang, sure, score

    try:
        lang, score = _langid_model.classify(text)
        if lang not in langs:
            langs[lang] = []
        langs[lang].append(score)
    except Exception as e:
        if warnings:
            logging.warning(e)

    if not langs:
        return 'un', False, 0.0

    scored = map(lambda x: (x[0], sum(x[1]) / len(x[1])), langs.items())
    lang, score = max(scored, key=operator.itemgetter(1))
    sure = len(langs[lang]) > 1 and score >= 0.75

    return lang, sure, score
