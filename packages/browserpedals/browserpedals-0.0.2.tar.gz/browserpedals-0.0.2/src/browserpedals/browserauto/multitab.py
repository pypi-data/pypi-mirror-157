import time
import json

from selenium.common.exceptions import (UnexpectedAlertPresentException, NoSuchWindowException,
                                        TimeoutException)


# This code relies on recordTabVisibility() function that is periodically called in site_setup.js
# The script get_tab_selection_time_script is read from get_tab_selection_time.js
# The driver is an instance of WebDriverEx class.


VISIBILITY_POLL_PERIOD_SEC = 1.5 # Set equal to VISIBILITY_POLL_PERIOD_MILLISEC in site_setup.js
VISIBILITY_WAIT_TIME_SEC = 1.5 # Set proportional to VISIBILITY_POLL_PERIOD_SEC


def to_active_tab(driver, get_tab_selection_time_script):
    current_tab_handle = driver.current_window_handle()
    if not current_tab_handle:
        return

    visibility_state = driver.execute_script("return document.visibilityState;",
                                             exceptions=(UnexpectedAlertPresentException,
                                                         NoSuchWindowException, TimeoutException))
    if (not visibility_state) or (visibility_state == "visible"):
        return

    tab_handles = driver.window_handles()
    if not tab_handles:
        return
    tabs_count = len(tab_handles)

    current_tab_index = tab_handles.index(current_tab_handle)

    if tabs_count == 2:
        if current_tab_index == 0:
            last_selected_tab_index = 1
        else:
            last_selected_tab_index = 0
        driver.switch_to.window(tab_handles[last_selected_tab_index])
        return

    # We will determine which tab is currently selected (visible, but not controlled by the driver).
    # It is one of the tabs which are set up to record tab recent visibility states.
    # (If there are tabs not yet set up to record tab recent visibility states, 
    # we will stop at first such tab and set it up.)
    # To achieve this, we will connect the driver to all tabs one by one.
    # For each tab we will then get it's recorded recent visibility states.
    # But before doing this, we will wait for some time longer than the JS visibility poll period
    # to let all tabs record their visibility states by JS.
    # Then we will connect the driver to all tabs one by one quickly, and we will ignore these
    # last visibility states because they will be the visibilities caused by driver connection.
    # We do not test the current tab (the one currently controlled by the driver but currently not visible).

    time.sleep(VISIBILITY_POLL_PERIOD_SEC + VISIBILITY_WAIT_TIME_SEC)
    recording_end_time_millisec = time.time() * 1000

    driver.switch_to.window(current_tab_handle)

    tab_selection_times = []

    i = current_tab_index
    while True:
        i = i + 1
        if i == tabs_count:
            i = 0
        if i == current_tab_index:
            break
        r = driver.switch_to.window(tab_handles[i])
        if not r:
            break

        tab_visibility_timestamps_str = driver.execute_script(get_tab_selection_time_script,
                                                              exceptions=(TimeoutException,))
        tab_visibility_timestamps_dict = None
        if tab_visibility_timestamps_str and (tab_visibility_timestamps_str != ""):
            try:
                tab_visibility_timestamps_dict = json.loads(tab_visibility_timestamps_str)
            except:
                tab_visibility_timestamps_dict = None
        if not tab_visibility_timestamps_dict:
            # This is a tab for which site_setup() has not been run yet.
            # Even if there are more than one such tabs, we will process them one at a time.
            # Return, so it stays controlled by the driver and selected,
            # and site_setup() will be called on it.
            return

        recent_visibility_timestamps = tab_visibility_timestamps_dict["recent_visibility_timestamps"]
        last_timestamp_index = tab_visibility_timestamps_dict["last_timestamp_index"]

        tab_selection_time_millisec = 0

        recent_visibility_timestamps_count = len(recent_visibility_timestamps)
        j = last_timestamp_index
        while True:
            j = j + 1
            if j == recent_visibility_timestamps_count:
                j = 0

            timestamp = recent_visibility_timestamps[j]

            test_time_millisec = timestamp["test_time"]
            tab_visibility = timestamp["tab_visibility"]

            condition = ((test_time_millisec < recording_end_time_millisec) and
                         (tab_visibility == "visible") and
                         (test_time_millisec > tab_selection_time_millisec))
            if condition:
                tab_selection_time_millisec = test_time_millisec

            if j == last_timestamp_index:
                break

        tab_selection_times.append((i, tab_selection_time_millisec))

    last_tab_selection_time = 0
    last_selected_tab_index = -1

    for tab_selection_info in tab_selection_times:
        if tab_selection_info[1] > last_tab_selection_time:
            last_tab_selection_time = tab_selection_info[1]
            last_selected_tab_index = tab_selection_info[0]

    if last_selected_tab_index >= 0:
        driver.switch_to.window(tab_handles[last_selected_tab_index])

