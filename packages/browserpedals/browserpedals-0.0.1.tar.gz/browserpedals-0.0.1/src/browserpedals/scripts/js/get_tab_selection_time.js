function getTabSelectionTime() {
    var dataStr = "";
    if (document.documentElement && document.documentElement.hasAttribute("data-tab-recent-visibility-timestamps")) {
        dataStr = document.documentElement.getAttribute("data-tab-recent-visibility-timestamps");
        if (!dataStr) {
            dataStr = "";
        }
    }
    return dataStr;
}

return getTabSelectionTime();

