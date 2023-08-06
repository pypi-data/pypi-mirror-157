import sys
from .i18n.languages import get_languages_dict


def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import termios    #for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)


class CmdlineUI:

    def on_pedal_pressed(self, role_name):
        if role_name == 'PausePedal':
            print("\n" + _("Pause/Play pedal pressed"), end='')
        elif role_name == 'JumpPedal':
            print("\n" + _("Jump Back pedal pressed"), end='')
        else:
            print("\n" + role_name + " pedal pressed", end='')
        return True

    def on_pedal_released(self, role_name):
        if role_name == 'PausePedal':
            print("\n" + _("Pause/Play pedal released"), end='')
        elif role_name == 'JumpPedal':
            print("\n" + _("Jump Back pedal released"), end='')
        else:
            print("\n" + role_name + " pedal released", end='')
        return True

    def on_timeout(self):
        return True


    def get_yes_from_user(self, msg, yes_name="Y", no_name="n"):
        flush_input()
        if (len(yes_name) > 0) and (len(no_name) > 0):
            if yes_name == "Y":
                yes_name = _("Y")
            if no_name == "n":
                no_name = _("n")
            keys_str = " (" + yes_name + "/" + no_name + ")"
        else:
            keys_str = _(" [Enter]")
        confirmed = input(msg + keys_str + "\n")
        if (len(yes_name) == 0) or (len(no_name) == 0):
            return True
        confirmed_low = confirmed.casefold()
        yes_name_low = yes_name.casefold()
        return (len(confirmed) == 0 or confirmed_low[-len(yes_name):] == yes_name_low)

    def show_progress_to_user(self, value, max_value, msg=""):
        if value < 0:
            print("", flush=True)
            return
        if len(msg) > 0:
            print(msg, flush=True)
            return
        print(".", end=' ', flush=True)

    def get_lang_from_user(self):
        flush_input()
        languages_list = []
        languages_dict = get_languages_dict()
        for lang, v in languages_dict.items():
            languages_list.append((lang, v["name"]))
        languages_str = ""
        for i in range(len(languages_list)):
            languages_str = languages_str + languages_list[i][1] + "(" + str(i) + ")"
            if i < (len(languages_list)-1):
                languages_str = languages_str + ", "
        languages_str = languages_str + " ?"
        confirmed = input(languages_str + "\n")
        if len(confirmed) != 1:
            return "en"
        try:
            i = int(confirmed[-1:])
        except:
            return "en"
        if (i >= 0) and (i < len(languages_list)):
            return languages_list[i][0]
        return "en"


