function checkUserInput() {
    const obj = {};

    if (document.getElementsByTagName("html")[0].hasAttribute("data-browserpedals-ui-button-clicked")) {
        var button = document.getElementsByTagName("html")[0].getAttribute("data-browserpedals-ui-button-clicked");
        if (!button) {
            button = "";
        }
        if (button != "") {
            if (document.getElementsByTagName("html")[0].hasAttribute("data-browserpedals-ui-select-changed")) {
                var selectedValue = document.getElementsByTagName("html")[0].getAttribute("data-browserpedals-ui-select-changed");
                if (!selectedValue) {
                    selectedValue = "";
                }
                if (selectedValue != "") {
                    document.getElementsByTagName("html")[0].removeAttribute("data-browserpedals-ui-select-changed");
                    obj["selected_value"] = selectedValue;
                }
            }

            document.getElementsByTagName("html")[0].removeAttribute("data-browserpedals-ui-button-clicked");
            obj["button_clicked"] = button;
        }
    }

    var informDiv = document.getElementById("BrowserpedalsUiInformDiv");
    if (informDiv) {
        if (informDiv.innerHTML == "") {
            obj["ui_state"] = "no_setup";
        }
    } else {
        obj["ui_state"] = "no_ui";
    }

    var resStr = JSON.stringify(obj);
    return resStr;
}

return checkUserInput();

