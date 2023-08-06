function zIndexInfo(elem, level, info) {
    if ((elem.id == "BrowserpedalsUiDiv") || 
    (elem.id == "BrowserpedalsUiInformDiv") || 
    (elem.id == "BrowserpedalsUiButtonsDiv") || 
    (elem.id == "BrowserpedalsUiProgressDiv") || 
    (elem.id == "BrowserpedalsUiEventsDiv") || 
    (elem.id == "BrowserpedalsUiNoDiv") || 
    (elem.id == "BrowserpedalsUiYesDiv") || 
    (elem.id == "BrowserpedalsUiYesButton") || 
    (elem.id == "BrowserpedalsUiNoButton") || 
    (elem.id == "BrowserpedalsUiProgressVal") || 
    (elem.id == "BrowserpedalsUiProgressText") || 
    (elem.id == "BrowserpedalsUiInformSelect"))
        return;

    var cssObj = window.getComputedStyle(elem, null);
    var indStr = cssObj.getPropertyValue("z-index");
    var ind = parseInt(indStr, 10);
    if (isNaN(ind)) {
        // total count of "auto" elements
        info[0] = info[0] + 1;
    } else {
        // maximum value of zIndex
        if (ind > info[1]) {
            info[1] = ind;
        }
    }
    var i;
    for (i = 0; i < elem.children.length; i++) {
        child = elem.children[i];
        zIndexInfo(child, level+1, info);
    }
}

var showOnTopCallCount = 0;

function showOnTop() {
    if (showOnTopCallCount > 0)
        return;
    showOnTopCallCount++;

    let info = [0, 0];
    zIndexInfo(document.body, 0, info);
    let zMax = info[1] + info[0];

    function showElemOnTop(elem_id) {
        let elem = document.getElementById(elem_id);
        if (elem) {
            zMax++;
            elem.style.zIndex = zMax.toString();
        }
    }

    showElemOnTop("BrowserpedalsUiDiv");
    showElemOnTop("BrowserpedalsUiInformDiv");
    showElemOnTop("BrowserpedalsUiButtonsDiv");
    showElemOnTop("BrowserpedalsUiProgressDiv");
    showElemOnTop("BrowserpedalsUiEventsDiv");
    showElemOnTop("BrowserpedalsUiNoDiv");
    showElemOnTop("BrowserpedalsUiYesDiv");
    showElemOnTop("BrowserpedalsUiYesButton");
    showElemOnTop("BrowserpedalsUiNoButton");
    showElemOnTop("BrowserpedalsUiProgressVal");
    showElemOnTop("BrowserpedalsUiProgressText");
    showElemOnTop("BrowserpedalsUiInformSelect");

    showOnTopCallCount--;
}

showOnTop();

