import sys
import time
import threading
import os

if sys.platform == "linux" or sys.platform == "linux2":
    from evdev import list_devices, InputDevice, ecodes
    import select
elif sys.platform == "darwin":
    pass
elif sys.platform == "win32":
    import pywinusb.hid as hid
    from pywinusb.hid import usage_pages

if __name__ == '__main__':
    from detect.detectpedals import read_dict, detect_pedals, choose_pedal_roles
    from detect.ui.cmdlineui import CmdlineUI
    from detect.ui.i18n.languages import init_languages, select_language
else:
    from .detect.detectpedals import read_dict, detect_pedals, choose_pedal_roles
    from .detect.ui.cmdlineui import CmdlineUI
    from .detect.ui.i18n.languages import init_languages, select_language


TEST_WAIT_SEC = 15.0
MONITOR_PERIOD_SEC = 1.5


pressed_sema = threading.BoundedSemaphore()


class PedalRole:

    def __init__(self, name):
        self.name = name
        self.clear_main()
        self.zero_count()

    def clear_main(self):
        self.device = None

        self.pedal_pressed_dict = None
        self.pedal_released_dict = None

        # Linux
        self.type = None
        self.code = None

        # Windows
        self.usage = None

    def zero_count(self):
        self.count = 0

    def get_pedals_data(self):
        if sys.platform == "linux" or sys.platform == "linux2":
            return (self.device.info.vendor, self.device.info.product, self.type, self.code)
        elif sys.platform == "darwin":
            return ()
        elif sys.platform == "win32":
            return (self.device.vendor_id, self.device.product_id, self.usage)


class Pedals:

    def __init__(self, dlg, is_test):
        values_list = choose_pedal_roles(dlg, is_test)
        self.roles = []
        for value in values_list:
            self.roles.append(PedalRole(value))
        self.clear_wrong()

    def refresh_roles(self):
        pedals_file_dict = read_dict()
        roles_dict = pedals_file_dict.get('roles')
        if not roles_dict:
            return
        values_list = roles_dict['values']
        self.roles = []
        for value in values_list:
            self.roles.append(PedalRole(value))

    def all_roles_have_devices(self):
        for role in self.roles:
            if not role.device:
                return False
        return True

    def device_is_in_a_role(self, device):
        for role in self.roles:
            if device == role.device:
                return True
        return False

    def close_all_devices(self):
        closed_devices = []
        for role in self.roles:
            if role.device and not (role.device in closed_devices):
                role.device.close()
                closed_devices.append(role.device)

    def clear_main(self):
        for role in self.roles:
            role.clear_main()

    def clear_wrong(self):
        self.wrong_pedals_list = []

    def zero_all_counts(self):
        for role in self.roles:
            role.zero_count()

    def all_counts_are_non_zero(self):
        for role in self.roles:
            if role.count == 0:
                return False
        return True

    def get_pedals_data(self):
        pedals_data = []
        for role in self.roles:
            pedals_data.append(role.get_pedals_data())
        return pedals_data


pedals = None

def refresh_roles_in_pedals():
    pedals.refresh_roles()


def find_pedals_linux(is_test, dlg):
    global pedals

    pedals_file_dict = None
    pedals_dict = None
    while True:
        pedals_file_dict = read_dict()
        pedals_dict = pedals_file_dict.get('pedals')
        if pedals_dict:
            break
        detect_pedals(refresh_roles_in_pedals, dlg)
    
    while True:
        pedals.clear_main()

        device_found = False

        for path in list_devices():
            device = InputDevice(path)
            if device.info.vendor == 0:
                # we ignore devices with Vendor ID zero
                device.close()
                continue
            device_dict = pedals_dict.get((device.info.vendor, device.info.product))
            if device_dict:
                os_dict = device_dict.get('linux')
                if os_dict:
                    capabilities_dict = device.capabilities(verbose=False, absinfo=False)
                    for role in pedals.roles:
                        condition = ((not role.device) and
                                     os_dict.get((role.name, 'Pressed')) and
                                     os_dict.get((role.name, 'Released')))
                        if condition:
                            pedal_pressed_dict = os_dict.get((role.name, 'Pressed'))
                            pedal_released_dict = os_dict.get((role.name, 'Released'))
                            for k in pedal_pressed_dict.keys():
                                event_type = k[0]
                                event_code = k[1]
                                code_list = capabilities_dict.get(event_type)
                                if code_list and (event_code in code_list):
                                    role.pedal_pressed_dict = pedal_pressed_dict
                                    role.pedal_released_dict = pedal_released_dict
                                    role.device = device
                                    role.type = event_type
                                    role.code = event_code
                                    if pedals.all_roles_have_devices():
                                        wrong_pedals_data = pedals.get_pedals_data()
                                        if not wrong_pedals_data in pedals.wrong_pedals_list:
                                            device_found = True
                                            break
                            if device_found:
                                break

            if not pedals.device_is_in_a_role(device):
                device.close()

        if device_found:
            break
        pedals.close_all_devices()
        is_yes = dlg.get_yes_from_user("\n" + _("Were the pedals plugged in?") + "\n" +
                                       _("If not, plug them in and then answer 'no'."))
        if is_yes:
            detect_pedals(refresh_roles_in_pedals, dlg)
            pedals_file_dict = read_dict()
            pedals_dict = pedals_file_dict.get('pedals')
            pedals.clear_wrong()


def find_pedals_mac(is_test, dlg):
    dlg.get_yes_from_user(_("Mac is not supported yet"), yes_name="")
    sys.exit()


def find_pedals_windows(is_test, dlg):
    global pedals

    pedals_file_dict = None
    pedals_dict = None
    while True:
        pedals_file_dict = read_dict()
        pedals_dict = pedals_file_dict.get('pedals')
        if pedals_dict:
            break
        detect_pedals(refresh_roles_in_pedals, dlg)
    
    while True:
        pedals.clear_main()

        device_found = False

        all_devices = hid.find_all_hid_devices()

        for device in all_devices:
            device.open()
            if device.vendor_id == 0:
                # we ignore devices with Vendor ID zero
                device.close()
                continue
            device_dict = pedals_dict.get((device.vendor_id, device.product_id))
            if device_dict:
                os_dict = device_dict.get('windows')
                if os_dict:
                    usages_dict = os_dict.get('usages')
                    if usages_dict:
                        all_input_reports = device.find_input_reports()
                        for input_report in all_input_reports:
                            for target_usage in input_report.keys():
                                page_id = hid.get_usage_page_id(target_usage)
                                usage_id = hid.get_short_usage_id(target_usage)
                                target_dict = usages_dict.get((page_id, usage_id))
                                if target_dict:
                                    for role in pedals.roles:
                                        condition = ((not role.device) and
                                                     target_dict.get((role.name, 'Pressed')) and
                                                     target_dict.get((role.name, 'Released')))
                                        if condition:
                                            role.pedal_pressed_dict = target_dict.get((role.name, 'Pressed'))
                                            role.pedal_released_dict = target_dict.get((role.name, 'Released'))
                                            role.device = device
                                            role.usage = target_usage
                                            if pedals.all_roles_have_devices():
                                                wrong_pedals_data = pedals.get_pedals_data()
                                                if not wrong_pedals_data in pedals.wrong_pedals_list:
                                                    device_found = True
                                                    break
                            if device_found:
                                break
            if device_found:
                break
            if not pedals.device_is_in_a_role(device):
                device.close()

        if device_found:
            break
        pedals.close_all_devices;
        is_yes = dlg.get_yes_from_user("\n" + _("Were the pedals plugged in?") + "\n" +
                                       _("If not, plug them in and then answer 'no'."))
        if is_yes:
            detect_pedals(refresh_roles_in_pedals, dlg)
            pedals_file_dict = read_dict()
            pedals_dict = pedals_file_dict.get('pedals')
            pedals.clear_wrong()


terminate = False

def do_read_pedals_linux(device, roles, is_main_thread, act, is_test, dlg):
    global pedals
    global terminate

    pedal_pressed = False

    start_time = time.time()
    test_time = 0
    while True:
        if is_test:
            if pedals.all_counts_are_non_zero():
                break
        if terminate:
            break
        r, w, x = select.select([device.fd], [], [], MONITOR_PERIOD_SEC)
        if ((r, w, x) == ([], [], [])) or (is_test and (test_time > TEST_WAIT_SEC)):
            #timeout
            if is_test:
                test_time = test_time + MONITOR_PERIOD_SEC
                if test_time > TEST_WAIT_SEC:
                    break
                if is_main_thread:
                    dlg.show_progress_to_user(test_time, TEST_WAIT_SEC)
            else:
                r = act.on_timeout()
                if not r:
                    terminate = True
        else:
            try:
                for event in device.read():
                    if is_test:
                        delta_time = event.sec - start_time
                        if delta_time > test_time:
                            test_time = delta_time
                        if test_time > TEST_WAIT_SEC:
                            break
                    if event and ((event.type == ecodes.EV_REL) or (event.type == ecodes.EV_ABS)):
                        for role in roles:
                            value_list = role.pedal_released_dict.get((event.type, event.code))
                            pedal_without_released = (value_list and len(value_list) == 0)

                            value_range = role.pedal_pressed_dict.get((event.type, event.code))
                            if value_range:
                                if (event.value >= value_range[0]) and (event.value <= value_range[1]):
                                    if (not pedal_pressed) or pedal_without_released:
                                        with pressed_sema:
                                            r = act.on_pedal_pressed(role.name)
                                            if not r:
                                                terminate = True
                                        if is_test:
                                            role.count = role.count + 1
                                        pedal_pressed = True
                    elif event and (event.type == ecodes.EV_KEY):
                        for role in roles:
                            value_list = role.pedal_released_dict.get((event.type, event.code))
                            pedal_without_released = (value_list and len(value_list) == 0)

                            value_list = role.pedal_pressed_dict.get((event.type, event.code))
                            if value_list:
                                if event.value in value_list:
                                    if (not pedal_pressed) or pedal_without_released:
                                        with pressed_sema:
                                            r = act.on_pedal_pressed(role.name)
                                            if not r:
                                                terminate = True
                                        if is_test:
                                            role.count = role.count + 1
                                        pedal_pressed = True

                    for role in roles:
                        value_list = role.pedal_released_dict.get((event.type, event.code))
                        if value_list:
                            if event.value in value_list:
                                if pedal_pressed:
                                    r = act.on_pedal_released(role.name)
                                    if not r:
                                        terminate = True
                                    pedal_pressed = False
            except OSError:
                #Pedals were unplugged
                pass


def read_pedals_linux(act, is_test, dlg):
    global pedals

    pedals.zero_all_counts()

    if is_test:
        dlg.show_progress_to_user(0, TEST_WAIT_SEC, "\n" + _("Testing the pedals...") +
                                  "\n" + _("During ") + str(TEST_WAIT_SEC) +
                                  _(" seconds press each pedal at least once.") + "\n")

    devices_with_roles_dict = dict()
    is_main_thread = True
    for role in pedals.roles:
        roles_dict = devices_with_roles_dict.get((role.device.info.vendor, role.device.info.product))
        if not roles_dict:
            roles_dict = dict()
            devices_with_roles_dict[(role.device.info.vendor, role.device.info.product)] = roles_dict
            roles_dict["device"] = role.device
            roles_dict["roles"] = []
            roles_dict["is_main_thread"] = is_main_thread
            is_main_thread = False
        roles_list = roles_dict["roles"]
        roles_list.append(role)

    for k, v in devices_with_roles_dict.items():
        if v["is_main_thread"]:
            continue
        v["thread"] = threading.Thread(target=do_read_pedals_linux,
                                       args=(v["device"], v["roles"], False, act, is_test, dlg))
        v["thread"].start()

    for k, v in devices_with_roles_dict.items():
        if v["is_main_thread"]:
            do_read_pedals_linux(v["device"], v["roles"], True, act, is_test, dlg)
            break

    for k, v in devices_with_roles_dict.items():
        if v["is_main_thread"]:
            continue
        while v["thread"].is_alive():
            v["thread"].join()
            time.sleep(0.3)

    res = True
    if is_test:
        dlg.show_progress_to_user(-1, TEST_WAIT_SEC)
        if pedals.all_counts_are_non_zero():
            dlg.get_yes_from_user("\n\n" + _("Pedals are working!"), yes_name="")
        else:
            res = False
            for role in pedals.roles:
                if role.count == 0:
                    wrong_pedals_data = pedals.get_pedals_data()
                    if not wrong_pedals_data in pedals.wrong_pedals_list:
                        pedals.wrong_pedals_list.append(wrong_pedals_data)

    pedals.close_all_devices()
    return res


def read_pedals_mac(act, is_test, dlg):
    dlg.get_yes_from_user(_("Mac is not supported yet"), yes_name="")
    sys.exit()


def read_pedals_windows(act, is_test, dlg):
    global pedals
    global terminate

    pedal_pressed = False

    pedals.zero_all_counts()

    def event_callback(event_value, event_type, callback_data):
        global pedals
        global terminate
        nonlocal pedal_pressed

        event_type = event_type #avoid pylint warnings

        pedal_pressed_func = callback_data[0]
        pedal_released_func = callback_data[1]
        roles = callback_data[2]

        for role in roles:
            pedal_without_released = False
            if len(role.pedal_released_dict['values']) == 0:
                pedal_without_released = True

            is_range = role.pedal_pressed_dict['is_range']
            if is_range:
                value_range = role.pedal_pressed_dict['values']
                if value_range and len(value_range) == 2:
                    if (event_value >= value_range[0]) and (event_value <= value_range[1]):
                        if (not pedal_pressed) or pedal_without_released:
                            with pressed_sema:
                                r = pedal_pressed_func(role.name)
                                if not r:
                                    terminate = True
                            if is_test:
                                role.count = role.count + 1
                            pedal_pressed = True
            else:
                value_list = role.pedal_pressed_dict['values']
                if value_list and (event_value in value_list):
                    if (not pedal_pressed) or pedal_without_released:
                        with pressed_sema:
                            r = pedal_pressed_func(role.name)
                            if not r:
                                terminate = True
                        if is_test:
                            role.count = role.count + 1
                        pedal_pressed = True
            value_list = role.pedal_released_dict['values']
            if value_list and (event_value in value_list):
                if pedal_pressed:
                    r = pedal_released_func(role.name)
                    if not r:
                        terminate = True
                    pedal_pressed = False

    devices_and_usages_with_roles_dict = dict()
    for role in pedals.roles:
        roles_dict = devices_and_usages_with_roles_dict.get((role.device.vendor_id, role.device.product_id, role.usage))
        if not roles_dict:
            roles_dict = dict()
            devices_and_usages_with_roles_dict[(role.device.vendor_id, role.device.product_id, role.usage)] = roles_dict
            roles_dict["device"] = role.device
            roles_dict["usage"] = role.usage
            roles_dict["roles"] = []
        roles_list = roles_dict["roles"]
        roles_list.append(role)

    for k, v in devices_and_usages_with_roles_dict.items():
        callback_data = (act.on_pedal_pressed, act.on_pedal_released, v["roles"])
        v["device"].add_event_handler(v["usage"],
            event_callback, hid.HID_EVT_CHANGED, callback_data)

    if is_test:
        dlg.show_progress_to_user(0, TEST_WAIT_SEC, "\n" + _("Testing the pedals...") +
                                  "\n" + _("During ") + str(TEST_WAIT_SEC) +
                                  _(" seconds press each pedal at least once.") + "\n")
    res = True
    test_time = 0
    while True:
        #just keep the device opened to receive events

        devices_are_plugged = True
        for role in pedals.roles:
            if not role.device.is_plugged():
                devices_are_plugged = False
                break
        if not devices_are_plugged:
            break

        time.sleep(MONITOR_PERIOD_SEC)
        if is_test:
            if pedals.all_counts_are_non_zero():
                dlg.show_progress_to_user(-1, TEST_WAIT_SEC)
                dlg.get_yes_from_user("\n\n" + _("Pedals are working!"), yes_name="")
                break
            test_time = test_time + MONITOR_PERIOD_SEC
            if test_time > TEST_WAIT_SEC:
                dlg.show_progress_to_user(-1, TEST_WAIT_SEC)
                for role in pedals.roles:
                    if role.count == 0:
                        wrong_pedals_data = pedals.get_pedals_data()
                        if not wrong_pedals_data in pedals.wrong_pedals_list:
                            pedals.wrong_pedals_list.append(wrong_pedals_data)
                res = False
                break
            dlg.show_progress_to_user(test_time, TEST_WAIT_SEC)
        else:
            r = act.on_timeout()
            if not r:
                terminate = True
        if terminate:
            break

    #Pedals were unplugged
    pedals.close_all_devices()
    return res


def read_or_find_pedals_linux(act, is_test, dlg):
    global pedals

    while True:
        res = read_pedals_linux(act, is_test, dlg)
        pedals.clear_main()

        if is_test and res:
            break
        if terminate:
            break
        time.sleep(1)
        find_pedals_linux(is_test, dlg)
        time.sleep(1)


def read_or_find_pedals_mac(act, is_test, dlg):
    dlg.get_yes_from_user(_("Mac is not supported yet"), yes_name="")
    sys.exit()


def read_or_find_pedals_windows(act, is_test, dlg):
    global pedals

    while True:
        res = read_pedals_windows(act, is_test, dlg)
        pedals.clear_main()

        if is_test and res:
            break
        if terminate:
            break
        time.sleep(1)
        find_pedals_windows(is_test, dlg)
        time.sleep(1)


def read_or_find_pedals(act=CmdlineUI(), is_test=True, dlg=CmdlineUI()):
    global pedals
    global terminate

    if not pedals:
        pedals = Pedals(dlg, is_test)

    terminate = False

    if is_test:
        is_yes = False
        while not is_yes:
            is_yes = dlg.get_yes_from_user("\n" + _("Now we will test the pedals.") +
                                           "\n" + _("Are you ready?"), no_name="")
    if sys.platform == "linux" or sys.platform == "linux2":
        find_pedals_linux(is_test, dlg)
        read_or_find_pedals_linux(act, is_test, dlg)
    elif sys.platform == "darwin":
        find_pedals_mac(is_test, dlg)
        read_or_find_pedals_mac(act, is_test, dlg)
    elif sys.platform == "win32":
        find_pedals_windows(is_test, dlg)
        read_or_find_pedals_windows(act, is_test, dlg)


if __name__ == '__main__':
    init_languages()
    select_language(CmdlineUI())
    read_or_find_pedals()

