var cssString = arguments[0];

function yesClicked() {
    document.getElementsByTagName("html")[0].setAttribute("data-browserpedals-ui-button-clicked", "yes");

    var informDiv = document.getElementById("BrowserpedalsUiInformDiv");
    informDiv.innerHTML = "";

    var yesDiv = document.getElementById("BrowserpedalsUiYesDiv");
    yesDiv.style.visibility = "hidden";

    var noDiv = document.getElementById("BrowserpedalsUiNoDiv");
    noDiv.style.visibility = "hidden";
}

function noClicked() {
    document.getElementsByTagName("html")[0].setAttribute("data-browserpedals-ui-button-clicked", "no");

    var informDiv = document.getElementById("BrowserpedalsUiInformDiv");
    informDiv.innerHTML = "";

    var yesDiv = document.getElementById("BrowserpedalsUiYesDiv");
    yesDiv.style.visibility = "hidden";

    var noDiv = document.getElementById("BrowserpedalsUiNoDiv");
    noDiv.style.visibility = "hidden";
}

var createDialogCallCount = 0;

function createPedalsDialog(cssStr) {
    if (createDialogCallCount > 0)
        return null;
    createDialogCallCount++;

    if (!document.getElementsByTagName("HEAD")[0]) {
        createDialogCallCount--;
        return null;
    }

    if (!document.body) {
        createDialogCallCount--;
        return null;
    }

    var styleElem = document.getElementById("BrowserpedalsUiStyle");
    if (!styleElem) {
        styleElem = document.createElement("STYLE");
        styleElem.id = "BrowserpedalsUiStyle";
        styleElem.innerHTML = cssStr;
        document.getElementsByTagName("HEAD")[0].appendChild(styleElem);
    }

    var wdiv = document.createElement("DIV");
    wdiv.id = "BrowserpedalsUiDiv";
    wdiv.className = "browserpedalsUiDivClass";
    document.body.appendChild(wdiv);


    var informDiv = document.createElement("DIV");
    informDiv.id = "BrowserpedalsUiInformDiv";
    informDiv.className = "browserpedalsUiInformDivClass";
    wdiv.appendChild(informDiv);

    var buttonsDiv = document.createElement("DIV");
    buttonsDiv.id = "BrowserpedalsUiButtonsDiv";
    buttonsDiv.className = "browserpedalsUiButtonsDivClass";
    wdiv.appendChild(buttonsDiv);

    var progressDiv = document.createElement("DIV");
    progressDiv.id = "BrowserpedalsUiProgressDiv";
    progressDiv.className = "browserpedalsUiProgressDivClass";
    progressDiv.style.visibility = "hidden";
    wdiv.appendChild(progressDiv);

    var eventsDiv = document.createElement("DIV");
    eventsDiv.id = "BrowserpedalsUiEventsDiv";
    eventsDiv.className = "browserpedalsUiEventsDivClass";
    wdiv.appendChild(eventsDiv);


    var noDiv = document.createElement("DIV");
    noDiv.id = "BrowserpedalsUiNoDiv";
    noDiv.className = "browserpedalsUiYesNoDivClass";
    noDiv.style.visibility = "hidden";
    buttonsDiv.appendChild(noDiv);

    var yesDiv = document.createElement("DIV");
    yesDiv.id = "BrowserpedalsUiYesDiv";
    yesDiv.className = "browserpedalsUiYesNoDivClass";
    yesDiv.style.visibility = "hidden";
    buttonsDiv.appendChild(yesDiv);


    var yesButton = document.createElement("BUTTON");
    yesButton.id = "BrowserpedalsUiYesButton";
    yesButton.className = "browserpedalsUiYesNoButtonClass";
    yesButton.type = "button";
    yesButton.innerText = "Yes";
    yesButton.onclick = yesClicked;
    yesDiv.appendChild(yesButton);

    var noButton = document.createElement("BUTTON");
    noButton.id = "BrowserpedalsUiNoButton";
    noButton.className = "browserpedalsUiYesNoButtonClass";
    noButton.type = "button";
    noButton.innerText = "No";
    noButton.onclick = noClicked;
    noDiv.appendChild(noButton);


    var progressVal = document.createElement("DIV");
    progressVal.id = "BrowserpedalsUiProgressVal";
    progressVal.className = "browserpedalsUiProgressValClass";

    progressVal.style.width = "1%"; // set progress value
    progressVal.style.height = "100%";

    progressDiv.appendChild(progressVal);

    var progressText = document.createElement("DIV");
    progressText.id = "BrowserpedalsUiProgressText";
    progressText.className = "browserpedalsUiProgressTextClass";

    progressText.style.margin = "-1%"; // set to minus progress value
    progressText.style.width = "100%";
    progressText.style.height = "100%";

    progressText.innerHTML = "1% of 15 sec"; // set progress value as text

    progressDiv.appendChild(progressText);

    createDialogCallCount--;

    return wdiv;
}

var wdiv = document.getElementById("BrowserpedalsUiDiv");
if (!wdiv) {
    wdiv = createPedalsDialog(cssString);
}

