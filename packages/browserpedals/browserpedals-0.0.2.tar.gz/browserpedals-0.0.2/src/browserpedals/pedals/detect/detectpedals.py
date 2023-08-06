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
    import auto_detected_pedals
    from ui.i18n.data_dirs.appdata import get_user_data_dir, install_resource
    from ui.cmdlineui import CmdlineUI
    from ui.i18n.languages import init_languages, select_language
else:
    from . import auto_detected_pedals
    from .ui.i18n.data_dirs.appdata import get_user_data_dir, install_resource
    from .ui.cmdlineui import CmdlineUI
    from .ui.i18n.languages import init_languages, select_language


TIMEOUT_SEC = 3.0
TOTAL_WAIT_SEC = 15.0
MONITOR_PERIOD_SEC = 1.5
USER_PREPARATION_SEC = 3.0


APP_DATA_DIR = get_user_data_dir()
PEDALS_FILE_NAME = 'auto_detected_pedals.txt'

pedals_file_path = install_resource(APP_DATA_DIR, auto_detected_pedals, PEDALS_FILE_NAME)


def dict2str(d, tab=0):
    s = ['{\n']
    for k,v in d.items():
        if isinstance(v, dict):
            v = dict2str(v, tab+1)
        else:
            v = repr(v)

        s.append('%s%r: %s,\n' % ('  '*tab, k, v))
    s.append('%s}' % ('  '*tab))
    return ''.join(s)

def write_dict(data):
    with open(pedals_file_path, 'w', encoding='utf_8') as f:
        f.write(dict2str(data))

def read_dict():
    try:
        with open(pedals_file_path, 'r', encoding='utf_8') as f:
            s = f.read()
            return eval(s)
    except FileNotFoundError:
        return dict()


def get_type_code_names(etype, ecode):
    type_name = ecodes.EV[etype]

    # ecodes.keys are a combination of KEY_ and BTN_ codes
    if etype == ecodes.EV_KEY:
        ecode_dict = ecodes.keys
    else:
        ecode_dict = getattr(ecodes, type_name.split('_')[-1])

    if ecode in ecode_dict:
        code_name = ecode_dict[ecode]
    else:
        code_name = "?"

    return (type_name, code_name)


def get_all_combinations(elements_list):
    if len(elements_list) == 0:
        return [[]]
    elem = elements_list[-1]
    combinations1 = get_all_combinations(elements_list[:-1])
    combinations2 = combinations1[:]
    for comb1 in combinations1:
        comb2 = comb1[:]
        comb2.append(elem)
        combinations2.append(comb2)
    return combinations2

def get_non_empty_combinations(elements_list):
    combinations1 = get_all_combinations(elements_list)
    combinations2 = []
    for i in range(len(elements_list), 0, -1):
        for comb1 in combinations1:
            if len(comb1) == i:
                combinations2.append(comb1)
    return combinations2

def get_role_title(role):
    if role == 'PausePedal':
        return _("Pause/Play pedal")
    elif role == 'JumpPedal':
        return _("Jump Back pedal")
    else:
        return role

def confirm_roles(values_list, dlg):
    role_names_str = ""
    for value in values_list:
        role_title = get_role_title(value)
        if len(role_names_str) == 0:
            role_names_str = role_title
        else:
            role_names_str = role_names_str + ", " + role_title

    is_yes = dlg.get_yes_from_user(_("All active pedal roles:") + "\n" + role_names_str + "\n",
                                   yes_name=_("OK"), no_name=_("Change"))
    return is_yes

def choose_pedal_roles(dlg, is_test=True):
    pedals_file_dict = read_dict()
    roles_dict = pedals_file_dict.get('roles')
    if not roles_dict:
        roles_dict = {
            'possible_values': ['PausePedal', 'JumpPedal'],
            'values': ['PausePedal', 'JumpPedal'],
            }
        pedals_file_dict['roles'] = roles_dict
        write_dict(pedals_file_dict)

    values_list = roles_dict['values']
    if is_test:
        if not confirm_roles(values_list, dlg):
            possible_values_list = roles_dict['possible_values']
            combinations_list = get_non_empty_combinations(possible_values_list)
            while True:
                for combination in combinations_list:
                    if confirm_roles(combination, dlg):
                        roles_dict['values'] = combination
                        write_dict(pedals_file_dict)
                        return combination
    return values_list


device_data_list = []

def read_device_events_linux(i):
    device_data = device_data_list[i]
    device = device_data['device']

    while True:
        with device_data['sema']:
            stop = device_data['stop']
        if stop:
            break
        r, w, x = select.select([device.fd], [], [], TIMEOUT_SEC)
        if (r, w, x) == ([], [], []):
            #timeout
            with device_data['sema']:
                if len(device_data['events_log']) > 0:
                    device_data['pressed'] = True
                    stop = True
            if stop:
                break
        else:
            for event in device.read():
                condition = (event and
                             ((event.type == ecodes.EV_KEY) or
                             (event.type == ecodes.EV_REL) or
                             (event.type == ecodes.EV_ABS)))
                if condition:
                    #we do not log synchronization events SynEvent(0)
                    #we log only KeyEvent(1), RelEvent(2), AbsEvent(3)
                    with device_data['sema']:
                        device_data['events_log'].append((event.type, event.code, event.value))


def roles_pedals_are_different_linux(os_dict, role1, role2):
    role1_pressed_dict = os_dict.get((role1, 'Pressed'))
    role2_pressed_dict = os_dict.get((role2, 'Pressed'))
    if role1_pressed_dict and role2_pressed_dict:
        for k1, v1 in role1_pressed_dict.items():
            event_type1 = k1[0]
            event_code1 = k1[1]
            for k2, v2 in role2_pressed_dict.items():
                event_type2 = k2[0]
                event_code2 = k2[1]
                if (event_type1 == event_type2) and (event_code1 == event_code2):
                    if (event_type1 == ecodes.EV_REL) or (event_type1 == ecodes.EV_ABS):
                        # value_range contains minimum and maximum value
                        role1_range = v1
                        if role1_range and (len(role1_range) == 2):
                            role2_range = v2
                            if role2_range and (len(role2_range) == 2):
                                if (role1_range[1] >= role2_range[0]) and (role1_range[0] <= role2_range[1]):
                                    return False
                    else:
                        role1_list = v1
                        if role1_list:
                            role2_list = v2
                            if role2_list:
                                for role2_value in role2_list:
                                    if role2_value in role1_list:
                                        return False
    return True

def process_events_log_linux(vendor, product, events_log, name, role, is_new_device, roles):
    pedals_file_dict = read_dict()

    pedals_dict = pedals_file_dict.get('pedals')
    if not pedals_dict:
        pedals_dict = dict()
        pedals_file_dict['pedals'] = pedals_dict

    device_dict = pedals_dict.get((vendor, product))
    if not device_dict:
        device_dict = dict()
        pedals_dict[(vendor, product)] = device_dict

    os_dict = device_dict.get('linux')
    was_detected_before = False
    if os_dict:
        was_detected_before = True
        for role2 in roles:
            if not os_dict.get((role2, 'Pressed')):
                was_detected_before = False
                break

    if not os_dict or is_new_device or was_detected_before:
        os_dict = dict()
        device_dict['linux'] = os_dict

    os_dict["name"] = name

    pedal_pressed_dict = dict()
    pedal_released_dict = dict()

    os_dict[(role, 'Pressed')] = pedal_pressed_dict
    os_dict[(role, 'Released')] = pedal_released_dict

    # Process all events except last one. Last one is 'Pedal Released'.
    for i in range(len(events_log)-1):
        event = events_log[i]
        event_type = event[0]
        event_code = event[1]
        event_value = event[2]

        if (event_type == ecodes.EV_REL) or (event_type == ecodes.EV_ABS):
            # value_range contains minimum and maximum value
            value_range = pedal_pressed_dict.get((event_type, event_code))
            if value_range:
                if event_value < value_range[0]:
                    value_range[0] = event_value
                if event_value > value_range[1]:
                    value_range[1] = event_value
            else:
                pedal_pressed_dict[(event_type, event_code)] = [event_value, event_value]
        else:
            # value_list contains the list of all values
            value_list = pedal_pressed_dict.get((event_type, event_code))
            if value_list:
                if not event_value in value_list:
                    value_list.append(event_value)
            else:
                pedal_pressed_dict[(event_type, event_code)] = [event_value]

    if len(events_log) > 1:
        # Last one is 'Pedal Released'.
        event = events_log[len(events_log)-1]
        event_type = event[0]
        event_code = event[1]
        event_value = event[2]

        value_list = pedal_released_dict.get((event_type, event_code))
        if value_list:
            if not event_value in value_list:
                value_list.append(event_value)
        else:
            pedal_released_dict[(event_type, event_code)] = [event_value]

        # Remove 'Pedal Released' if by chance it is present (if pedal was pressed several times).
        if (event_type == ecodes.EV_REL) or (event_type == ecodes.EV_ABS):
            # value_range contains minimum and maximum value
            value_range = pedal_pressed_dict.get((event_type, event_code))
            if event_value == value_range[0]:
                value_range[0] = event_value + 1
            if event_value == value_range[1]:
                value_range[1] = event_value - 1
            if value_range[0] > value_range[1]:
                raise ValueError
        else:
            # value_list contains the list of all values
            value_list = pedal_pressed_dict.get((event_type, event_code))
            while event_value in value_list:
                value_list.remove(event_value)
            if len(value_list) < 1:
                raise ValueError
    else:
        event = events_log[len(events_log)-1]
        event_type = event[0]
        event_code = event[1]
        event_value = event[2]

        value_list = pedal_pressed_dict.get((event_type, event_code))
        if value_list:
            if not event_value in value_list:
                value_list.append(event_value)
            if len(value_list) != 1:
                raise ValueError
        else:
            pedal_pressed_dict[(event_type, event_code)] = [event_value]

    # Different roles pedals should not be the same
    for role2 in roles:
        if role2 == role:
            continue
        if not roles_pedals_are_different_linux(os_dict, role, role2):
            return False

    write_dict(pedals_file_dict)
    return True


def roles_pedals_are_different_windows(target_dict, role1, role2):
    role1_pressed_dict = target_dict.get((role1, 'Pressed'))
    role2_pressed_dict = target_dict.get((role2, 'Pressed'))
    if role1_pressed_dict and role2_pressed_dict:
        if role1_pressed_dict['is_range']:
            role1_range = role1_pressed_dict['values']
            if role1_range and (len(role1_range) == 2):
                if role2_pressed_dict['is_range']:
                    role2_range = role2_pressed_dict['values']
                    if role2_range and (len(role2_range) == 2):
                        if (role1_range[1] >= role2_range[0]) and (role1_range[0] <= role2_range[1]):
                            return False
                else:
                    role2_list = role2_pressed_dict['values']
                    if role2_list:
                        for role2_value in role2_list:
                            if (role2_value >= role1_range[0]) and (role2_value <= role1_range[1]):
                                return False
        else:
            role1_list = role1_pressed_dict['values']
            if role1_list:
                if role2_pressed_dict['is_range']:
                    role2_range = role2_pressed_dict['values']
                    if role2_range and (len(role2_range) == 2):
                        for role1_value in role1_list:
                            if (role1_value >= role2_range[0]) and (role1_value <= role2_range[1]):
                                return False
                else:
                    role2_list = role2_pressed_dict['values']
                    if role2_list:
                        for role2_value in role2_list:
                            if role2_value in role1_list:
                                return False
    return True

def process_events_log_windows(vendor, product, target_usage, is_range, events_log, name, role, is_new_device, roles):
    pedals_file_dict = read_dict()

    pedals_dict = pedals_file_dict.get('pedals')
    if not pedals_dict:
        pedals_dict = dict()
        pedals_file_dict['pedals'] = pedals_dict

    device_dict = pedals_dict.get((vendor, product))
    if not device_dict:
        device_dict = dict()
        pedals_dict[(vendor, product)] = device_dict

    os_dict = device_dict.get('windows')
    if not os_dict:
        os_dict = dict()
        device_dict['windows'] = os_dict

    os_dict["name"] = name

    usages_dict = os_dict.get('usages')
    if not usages_dict or is_new_device:
        usages_dict = dict()
        os_dict['usages'] = usages_dict

    page_id = hid.get_usage_page_id(target_usage)
    usage_id = hid.get_short_usage_id(target_usage)

    target_dict = usages_dict.get((page_id, usage_id))
    if not target_dict:
        target_dict = dict()
        usages_dict[(page_id, usage_id)] = target_dict

    target_dict['name'] = repr(usage_pages.HidUsage(page_id, usage_id))

    pedal_pressed_list = []
    pedal_released_list = []

    pedal_pressed_dict = target_dict.get((role, 'Pressed'))
    if not pedal_pressed_dict:
        pedal_pressed_dict = dict()
        target_dict[(role, 'Pressed')] = pedal_pressed_dict
    if is_range:
        pedal_pressed_dict['is_range'] = 1
    else:
        pedal_pressed_dict['is_range'] = 0
    pedal_pressed_dict['values'] = pedal_pressed_list

    pedal_released_dict = target_dict.get((role, 'Released'))
    if not pedal_released_dict:
        pedal_released_dict = dict()
        target_dict[(role, 'Released')] = pedal_released_dict
    pedal_released_dict['values'] = pedal_released_list

    # Process all events except last one. Last one is 'Pedal Released'.
    for i in range(len(events_log)-1):
        event_value = events_log[i]

        if is_range:
            # value_range contains minimum and maximum value
            while len(pedal_pressed_list) < 2:
                pedal_pressed_list.append(event_value)
            if event_value < pedal_pressed_list[0]:
                pedal_pressed_list[0] = event_value
            if event_value > pedal_pressed_list[1]:
                pedal_pressed_list[1] = event_value
        else:
            # value_list contains the list of all values
            if not event_value in pedal_pressed_list:
                pedal_pressed_list.append(event_value)

    if len(events_log) > 1:
        # Last one is 'Pedal Released'.
        event_value = events_log[len(events_log)-1]
        if not event_value in pedal_released_list:
            pedal_released_list.append(event_value)

        # Remove 'Pedal Released' if by chance it is present (if pedal was pressed several times).
        if is_range:
            if event_value == pedal_pressed_list[0]:
                pedal_pressed_list[0] = event_value + 1
            if event_value == pedal_pressed_list[1]:
                pedal_pressed_list[1] = event_value - 1
            if pedal_pressed_list[0] > pedal_pressed_list[1]:
                raise ValueError
        else:
            while event_value in pedal_pressed_list:
                pedal_pressed_list.remove(event_value)
            if len(pedal_pressed_list) < 1:
                raise ValueError
    else:
        event_value = events_log[len(events_log)-1]
        if not event_value in pedal_pressed_list:
            pedal_pressed_list.append(event_value)
        if len(pedal_pressed_list) != 1:
            raise ValueError

    # Different roles pedals should not be the same
    for role2 in roles:
        if role2 == role:
            continue
        if not roles_pedals_are_different_windows(target_dict, role, role2):
            return False

    write_dict(pedals_file_dict)
    return True


def start_device_threads_linux():
    global device_data_list

    device_data_list = []

    for path in list_devices():
        device = InputDevice(path)
        if device.info.vendor == 0:
            # we ignore devices with Vendor ID zero
            device.close()
            continue

        i = len(device_data_list)

        device_data = dict()
        device_data_list.append(device_data)

        thread = threading.Thread(target=read_device_events_linux, args=(i,))

        device_data['device'] = device
        device_data['thread'] = thread
        device_data['vendor'] = device.info.vendor
        device_data['product'] = device.info.product
        device_data['events_log'] = []
        device_data['stop'] = False
        device_data['name'] = device.name
        device_data['pressed'] = False
        device_data['sema'] = threading.BoundedSemaphore()

        thread.start()


def stop_device_threads_linux(role, is_new_device, dlg, roles):
    global device_data_list

    for i in range(len(device_data_list)):
        device_data = device_data_list[i]
        with device_data['sema']:
            device_data['stop'] = True

    time.sleep(TIMEOUT_SEC)

    for i in range(len(device_data_list)):
        device_data = device_data_list[i]
        device = device_data['device']
        thread = device_data['thread']
        while thread.is_alive():
            thread.join()
            time.sleep(0.3)
        device.close()

    done = False
    for i in range(len(device_data_list)):
        device_data = device_data_list[i]
        pressed = device_data['pressed']
        if pressed:
            vendor = device_data['vendor']
            product = device_data['product']
            events_log = device_data['events_log']
            name = device_data['name']
            event = events_log[0]
            event_type = event[0]
            event_code = event[1]
            is_yes = dlg.get_yes_from_user("\n" +
                                           "VID: " + str(hex(vendor)) + ", " +
                                           "PID: " + str(hex(product)) + ", " +
                                           str(get_type_code_names(event_type, event_code)) + "\n" +
                                           name + "\n" +
                                           "\n" + _("Is this device correct?"))
            if is_yes:
                done = process_events_log_linux(vendor, product, events_log, name, role, is_new_device, roles)
                if done:
                    dlg.get_yes_from_user("\n" + _("Saved") + "\n" + pedals_file_path, yes_name="")
                    break
    device_data_list = []
    return done


def close_devices_windows(role, is_new_device, dlg, roles):
    global device_data_list

    for i in range(len(device_data_list)):
        device_data = device_data_list[i]
        device = device_data['device']
        device.close()
        device_data['close_time'] = time.time()

    done = False
    for i in range(len(device_data_list)):
        device_data = device_data_list[i]
        vendor = device_data['vendor']
        product = device_data['product']
        name = device_data['name']
        usages_dict = device_data['usages']
        close_time = device_data['close_time']
        for target_usage, usage_data in usages_dict.items():
            events_log = usage_data['events_log']
            last_event_time = usage_data['last_event_time']
            if (len(events_log) > 0) and (close_time - last_event_time > TIMEOUT_SEC):
                is_range = usage_data['is_range']
                page_id = hid.get_usage_page_id(target_usage)
                usage_id = hid.get_short_usage_id(target_usage)
                is_yes = dlg.get_yes_from_user("\n" + 
                                               "VID: " + str(hex(vendor)) + ", " +
                                               "PID: " + str(hex(product)) + ", " +
                                               repr(usage_pages.HidUsage(page_id, usage_id)) + "\n" +
                                               name + "\n" +
                                               "\n" + _("Is this device correct?"))
                if is_yes:
                    done = process_events_log_windows(vendor, product, target_usage, is_range,
                                                      events_log, name, role, is_new_device, roles)
                    if done:
                        dlg.get_yes_from_user("\n" + _("Saved") + "\n" + pedals_file_path, yes_name="")
                        break
        if done:
            break
    device_data_list = []
    return done


def monitor_devices_linux(dlg, role, is_new_device, roles):
    dlg.get_yes_from_user('\n' + _('Detect') + ' ' + get_role_title(role) + '\n' +
                          '\n' + _('Wait for the prompt "Press and release') + ' ' + get_role_title(role) + '".' + '\n' +
                          _('Do not press any other buttons and do not move the mouse.'), yes_name="")
    time.sleep(USER_PREPARATION_SEC)

    start_device_threads_linux()

    threads_count = 0
    for i in range(len(device_data_list)):
        device_data = device_data_list[i]
        thread = device_data['thread']
        if thread.is_alive():
            threads_count = threads_count + 1

    if threads_count == 0:
        dlg.get_yes_from_user(_("Sorry, no HID devices found"), yes_name="")
        stop_device_threads_linux(role, is_new_device, dlg, roles)
        return False

    time.sleep(1.0)
    for i in range(len(device_data_list)):
        device_data = device_data_list[i]
        # we discard first events logged after starting the threads
        with device_data['sema']:
            device_data['events_log'] = []

    dlg.show_progress_to_user(0, TOTAL_WAIT_SEC, "\n" + _("Press and release") + " " + get_role_title(role) + "\n")

    j = 0
    pedal_was_pressed = False
    while (j * MONITOR_PERIOD_SEC) < TOTAL_WAIT_SEC:
        time.sleep(MONITOR_PERIOD_SEC)
        for i in range(len(device_data_list)):
            device_data = device_data_list[i]
            with device_data['sema']:
                if device_data['pressed']:
                    pedal_was_pressed = True
            if pedal_was_pressed:
                break
        if pedal_was_pressed:
            break
        dlg.show_progress_to_user((j * MONITOR_PERIOD_SEC), TOTAL_WAIT_SEC)
        j = j + 1
    dlg.show_progress_to_user(-1, TOTAL_WAIT_SEC)
    if not pedal_was_pressed:
        dlg.get_yes_from_user(_("Pedal was not pressed (or something else like joystick was constantly pressed)"), yes_name="")
    res = stop_device_threads_linux(role, is_new_device, dlg, roles)
    return res


def monitor_devices_mac(dlg, role, is_new_device, roles):
    dlg.get_yes_from_user(_("Mac is not supported yet"), yes_name="")
    sys.exit()


def monitor_devices_windows(dlg, role, is_new_device, roles):
    global device_data_list

    dlg.get_yes_from_user('\n' + _('Detect') + ' ' + get_role_title(role) + '\n' +
                          '\n' + _('Wait for the prompt "Press and release') + ' ' + get_role_title(role) + '".' + '\n' +
                          _('Do not press any other buttons and do not move the mouse.'), yes_name="")
    time.sleep(USER_PREPARATION_SEC)

    device_data_list = []

    def event_callback(event_value, event_type, data_tuple):
        i = data_tuple[0]
        target_usage = data_tuple[1]

        device_data = device_data_list[i]
        usages_dict = device_data['usages']
        usage_data = usages_dict[target_usage]
        events_log = usage_data['events_log']
        
        event_type = event_type #avoid pylint warnings

        with usage_data['sema']:
            events_log.append(event_value)
            usage_data['last_event_time'] = time.time()

    all_devices = hid.find_all_hid_devices()

    for device in all_devices:
        device.open()
        if device.vendor_id == 0:
            # we ignore devices with Vendor ID zero
            device.close()
            continue

        i = len(device_data_list)

        device_data = dict()
        device_data_list.append(device_data)

        device_data['device'] = device
        device_data['vendor'] = device.vendor_id
        device_data['product'] = device.product_id
        device_data['name'] = device.vendor_name + " : " + device.product_name

        usages_dict = dict()
        device_data['usages'] = usages_dict

        all_input_reports = device.find_input_reports()

        for input_report in all_input_reports:
            for target_usage, v in input_report.items():
                usage_data = usages_dict.get(target_usage)
                if not usage_data:
                    usage_data = dict()
                    usages_dict[target_usage] = usage_data

                    usage_data['is_range'] = v.is_value() and not v.is_value_array()
                    usage_data['events_log'] = []
                    usage_data['last_event_time'] = 0
                    usage_data['sema'] = threading.BoundedSemaphore()

    logs_count = 0
    for i in range(len(device_data_list)):
        device_data = device_data_list[i]
        device = device_data['device']
        usages_dict = device_data['usages']
        for target_usage in usages_dict.keys():
            logs_count = logs_count + 1

            # add event handler (example of other available
            # events: EVT_PRESSED, EVT_RELEASED, EVT_ALL, HID_EVT_CHANGED, ...)
            device.add_event_handler(target_usage,
                event_callback, hid.HID_EVT_CHANGED, (i,target_usage)) #level usage

    if logs_count == 0:
        dlg.get_yes_from_user(_("Sorry, no HID devices found"), yes_name="")
        close_devices_windows(role, is_new_device, dlg, roles)
        return False

    time.sleep(1.0)
    for i in range(len(device_data_list)):
        device_data = device_data_list[i]
        usages_dict = device_data['usages']
        for k, usage_data in usages_dict.items():
            # we discard first events logged after registering the callback
            with usage_data['sema']:
                usage_data['events_log'] = []
                usage_data['last_event_time'] = 0

    dlg.show_progress_to_user(0, TOTAL_WAIT_SEC, "\n" + _("Press and release") + " " + get_role_title(role) + "\n")

    j = 0
    pedal_was_pressed = False
    while (j * MONITOR_PERIOD_SEC) < TOTAL_WAIT_SEC:
        time.sleep(MONITOR_PERIOD_SEC)
        for i in range(len(device_data_list)):
            device_data = device_data_list[i]
            usages_dict = device_data['usages']
            for k, usage_data in usages_dict.items():
                with usage_data['sema']:
                    events_log = usage_data['events_log']
                    log_present = (len(events_log) > 0)
                    last_event_time = usage_data['last_event_time']
                current_time = time.time()
                if log_present and (current_time - last_event_time > TIMEOUT_SEC):
                    pedal_was_pressed = True
                    break
            if pedal_was_pressed:
                break
        if pedal_was_pressed:
            break
        dlg.show_progress_to_user((j * MONITOR_PERIOD_SEC), TOTAL_WAIT_SEC)
        j = j + 1
    dlg.show_progress_to_user(-1, TOTAL_WAIT_SEC)
    if not pedal_was_pressed:
        dlg.get_yes_from_user(_("Pedal was not pressed (or something else like joystick was constantly pressed)"), yes_name="")
    res = close_devices_windows(role, is_new_device, dlg, roles)
    return res


def refresh_externals():
    pass

def detect_pedals(refresh_externals_func, dlg=CmdlineUI()):
    roles = choose_pedal_roles(dlg)
    refresh_externals_func()

    is_yes = False
    while not is_yes:
        is_yes = dlg.get_yes_from_user("\n" + _("Now we will detect the pedals.") +
                                       "\n" + _("Each pedal will be detected during ") + str(TOTAL_WAIT_SEC) + _(" seconds.") +
                                       "\n" + _("Are you ready?"), no_name="")

    is_new_device = True
    for role in roles:
        if sys.platform == "linux" or sys.platform == "linux2":
            res = monitor_devices_linux(dlg, role, is_new_device, roles)
        elif sys.platform == "darwin":
            res = monitor_devices_mac(dlg, role, is_new_device, roles)
        elif sys.platform == "win32":
            res = monitor_devices_windows(dlg, role, is_new_device, roles)
        if not res:
            break
        is_new_device = False

    return res


if __name__ == '__main__':
    init_languages()
    select_language(CmdlineUI())
    detect_pedals(refresh_externals)
