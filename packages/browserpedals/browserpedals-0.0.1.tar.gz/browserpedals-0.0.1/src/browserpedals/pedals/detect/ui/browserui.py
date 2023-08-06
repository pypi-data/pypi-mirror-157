import os
import json
import time

from selenium.common.exceptions import (NoSuchWindowException, UnexpectedAlertPresentException)
from . import dialog
from .i18n.data_dirs.appdata import get_user_data_dir, install_and_read_resource
from .i18n.languages import set_language, get_languages_dict, get_language

#try:
#    import importlib.resources as dist_resources
#except ImportError:
    # Try backported to PY<37 `importlib_resources`.
import importlib_resources as dist_resources


SHORT_POLL_PERIOD_SEC = 0.3
LONG_POLL_PERIOD_SEC = 1.5
FAST_POLL_TIME_SEC = 30.0
Z_CALL_PERIOD_SEC = 5.0


JS_DIR = "js"
CSS_DIR = "css"

UI_OPEN_CSS_FILE_NAME = "ui_open.css"

UI_OPEN_JS_FILE_NAME = "ui_open.js"
UI_CLOSE_JS_FILE_NAME = "ui_close.js"
UI_ON_EVENT_JS_FILE_NAME = "ui_on_event.js"
UI_SHOW_PROGRESS_JS_FILE_NAME = "ui_show_progress.js"
UI_SETUP_BUTTONS_JS_FILE_NAME = "ui_setup_buttons.js"
UI_CHECK_USER_INPUT_JS_FILE_NAME = "ui_check_user_input.js"
UI_Z_INDEX_JS_FILE_NAME = "ui_z_index.js"


APP_DATA_DIR = get_user_data_dir()


ui_open_css = install_and_read_resource(os.path.join(APP_DATA_DIR, CSS_DIR), 
                                        dialog, UI_OPEN_CSS_FILE_NAME, JS_DIR, CSS_DIR)
ui_open_css_file_path = os.path.join(APP_DATA_DIR, CSS_DIR, UI_OPEN_CSS_FILE_NAME)

ui_open_script = dist_resources.files(dialog).joinpath(JS_DIR).joinpath(UI_OPEN_JS_FILE_NAME).read_text(encoding='utf-8')

ui_close_script = dist_resources.files(dialog).joinpath(JS_DIR).joinpath(UI_CLOSE_JS_FILE_NAME).read_text(encoding='utf-8')

ui_on_event_script = dist_resources.files(dialog).joinpath(JS_DIR).joinpath(UI_ON_EVENT_JS_FILE_NAME).read_text(encoding='utf-8')

ui_show_progress_script = dist_resources.files(dialog).joinpath(JS_DIR).joinpath(UI_SHOW_PROGRESS_JS_FILE_NAME).read_text(encoding='utf-8')

ui_setup_buttons_script = dist_resources.files(dialog).joinpath(JS_DIR).joinpath(UI_SETUP_BUTTONS_JS_FILE_NAME).read_text(encoding='utf-8')

ui_check_user_input_script = dist_resources.files(dialog).joinpath(JS_DIR).joinpath(UI_CHECK_USER_INPUT_JS_FILE_NAME).read_text(encoding='utf-8')

ui_z_index_script = dist_resources.files(dialog).joinpath(JS_DIR).joinpath(UI_Z_INDEX_JS_FILE_NAME).read_text(encoding='utf-8')


def process_string(msg):
    msg2 = msg.replace("\r\n", "\n")
    msg3 = msg2.replace("\r", "\n")
    while True:
        msg4 = msg3.replace("\n ", "\n")
        if len(msg4) == len(msg3):
            break
        msg3 = msg4
    while True:
        msg4 = msg3.replace(" \n", "\n")
        if len(msg4) == len(msg3):
            break
        msg3 = msg4
    while True:
        msg4 = msg3.replace("\t\n", "\n")
        if len(msg4) == len(msg3):
            break
        msg3 = msg4
    while True:
        msg4 = msg3.replace("\n\t", "\n")
        if len(msg4) == len(msg3):
            break
        msg3 = msg4
    while True:
        msg4 = msg3.replace("\n\n", "\n")
        if len(msg4) == len(msg3):
            break
        msg3 = msg4
    msg4 = msg3.replace("\n", "<br>")
    return msg4


class BrowserDialogUI:

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.execute_script(ui_open_script, ui_open_css)

    def close(self):
        self.driver.wait_for_page()
        self.driver.execute_script(ui_close_script)

    def _wait_for_user_input(self, args):
        poll_period = SHORT_POLL_PERIOD_SEC
        start_time = time.time()
        z_call_time = time.time()

        while True:
            resStr = self.driver.execute_script(ui_check_user_input_script,
                                                exceptions=(NoSuchWindowException,
                                                            UnexpectedAlertPresentException))
            if not resStr:
                resStr = ""

            resDict = None
            if resStr and (resStr != ""):
                try:
                    resDict = json.loads(resStr)
                except:
                    pass

            if resDict:
                ui_state = resDict.get("ui_state")
                if ui_state and ui_state == "no_ui":
                    self.open()
                    poll_period = SHORT_POLL_PERIOD_SEC
                    start_time = time.time()
                    time.sleep(LONG_POLL_PERIOD_SEC)
                    continue

                lang = args.get("lang")
                if lang:
                    button_clicked = resDict.get("button_clicked")
                    if button_clicked and button_clicked != "":
                        if (button_clicked == "yes"):
                            selected_lang = resDict.get("selected_value")
                            if selected_lang and selected_lang != "":
                                return selected_lang
                            else:
                                return lang
                        else:
                            return lang

                    if ui_state and ui_state == "no_setup":
                        languages_list = args.get("lang_list")
                        self.driver.execute_script(ui_setup_buttons_script, "", "OK",
                                                   "", json.dumps(languages_list), lang)
                        poll_period = SHORT_POLL_PERIOD_SEC
                        start_time = time.time()
                        time.sleep(LONG_POLL_PERIOD_SEC)
                        continue

                msg = args.get("msg")
                if msg:
                    button_clicked = resDict.get("button_clicked")
                    if button_clicked and button_clicked != "":
                        return button_clicked

                    if ui_state and ui_state == "no_setup":
                        yes_name = args.get("yes_name")
                        no_name = args.get("no_name")
                        self.driver.execute_script(ui_setup_buttons_script, msg, yes_name, no_name)
                        poll_period = SHORT_POLL_PERIOD_SEC
                        start_time = time.time()
                        time.sleep(LONG_POLL_PERIOD_SEC)
                        continue

            current_time = time.time()
            if current_time - z_call_time > Z_CALL_PERIOD_SEC:
                self.driver.execute_script(ui_z_index_script, exceptions=(NoSuchWindowException,
                                                                          UnexpectedAlertPresentException))
                z_call_time = time.time()

            if poll_period == SHORT_POLL_PERIOD_SEC:
                current_time = time.time()
                if current_time - start_time > FAST_POLL_TIME_SEC:
                    poll_period = LONG_POLL_PERIOD_SEC

            time.sleep(poll_period)
        return None


    def on_pedal_pressed(self, role_name):
        self.driver.wait_for_page()
        if role_name == 'PausePedal':
            self.driver.execute_script(ui_on_event_script, _("Pause/Play pedal pressed"))
        elif role_name == 'JumpPedal':
            self.driver.execute_script(ui_on_event_script, _("Jump Back pedal pressed"))
        else:
            self.driver.execute_script(ui_on_event_script, role_name + "Pressed")
        return True

    def on_pedal_released(self, role_name):
        self.driver.wait_for_page()
        if role_name == 'PausePedal':
            self.driver.execute_script(ui_on_event_script, _("Pause/Play pedal released"))
        elif role_name == 'JumpPedal':
            self.driver.execute_script(ui_on_event_script, _("Jump Back pedal released"))
        else:
            self.driver.execute_script(ui_on_event_script, role_name + "Released")
        return True

    def on_timeout(self):
        return True


    def get_yes_from_user(self, msg, yes_name="Yes", no_name="No"):
        yes_name2 = yes_name
        no_name2 = no_name
        if yes_name == "Yes":
            yes_name2 = _("Yes")
        if no_name == "No":
            no_name2 = _("No")
        if len(yes_name) == 0:
            yes_name2 = "OK"
            no_name2 = ""
        msg2 = process_string(msg)

        args = {"msg":msg2, "yes_name":yes_name2, "no_name":no_name2}
        button_clicked = self._wait_for_user_input(args)
        return (button_clicked == "yes")

    def show_progress_to_user(self, value, max_value, msg=""):
        msg2 = process_string(msg)
        self.driver.execute_script(ui_show_progress_script, value, max_value, msg2,
                                   exceptions=(NoSuchWindowException, UnexpectedAlertPresentException))

    def get_lang_from_user(self):
        languages_list = []
        languages_dict = get_languages_dict()
        for lang, v in languages_dict.items():
            languages_list.append((lang, v["name"]))
        lang = get_language()

        args = {"lang_list":languages_list, "lang":lang}
        return self._wait_for_user_input(args)

