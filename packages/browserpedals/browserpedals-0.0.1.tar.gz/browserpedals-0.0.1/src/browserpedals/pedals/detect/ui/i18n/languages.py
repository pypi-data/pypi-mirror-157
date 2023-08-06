import os
import gettext

#try:
#    import importlib.resources as dist_resources
#except ImportError:
    # Try backported to PY<37 `importlib_resources`.
import importlib_resources as dist_resources

from . import language_names, locale
from .data_dirs.appdata import get_user_data_dir, install_resource

LANGUAGES_FILE_NAME = "language_names.txt"
LOCALE_DIR_NAME = "locale"
MO_FILE_NAME = "browserpedals.mo"

s = dist_resources.files(language_names).joinpath(LANGUAGES_FILE_NAME).read_text(encoding='utf-8')
languages_dict = eval(s)['languages']

def init_languages():
    app_data_dir = get_user_data_dir()
    locale_dir = os.path.join(app_data_dir, LOCALE_DIR_NAME)
    for lang, v in languages_dict.items():
        lang_dir = os.path.join(locale_dir, lang, "LC_MESSAGES")
        install_resource(lang_dir, locale, MO_FILE_NAME, lang, "LC_MESSAGES")
        v["translation"] = gettext.translation('browserpedals', localedir=locale_dir, languages=[lang], fallback=True)

current_language = None

def set_language(lang):
    global current_language

    v = languages_dict.get(lang)
    if v:
        current_language = lang
        t = v.get("translation")
        if t:
            t.install()
            return
    gettext.NullTranslations().install()

def get_language():
    return current_language

def get_languages_dict():
    return languages_dict

def select_language(dlg):
    lang = dlg.get_lang_from_user()
    set_language(lang)

