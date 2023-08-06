var infoString = arguments[0];
var yesName = arguments[1];
var noName = arguments[2];
var infoItems = [];
var infoSelected = "";
if (arguments.length > 3)
    var infoItems = arguments[3];
if (arguments.length > 4)
    var infoSelected = arguments[4];

function selectChanged() {
    var value = document.getElementById("BrowserpedalsUiInformSelect").value;
    document.getElementsByTagName("html")[0].setAttribute("data-browserpedals-ui-select-changed", value);
}

var setupButtonsCallCount = 0;

function setupButtons() {
    if (setupButtonsCallCount > 0)
        return;
    setupButtonsCallCount++;

    document.getElementsByTagName("html")[0].setAttribute("data-browserpedals-ui-button-clicked", "");
    document.getElementsByTagName("html")[0].setAttribute("data-browserpedals-ui-select-changed", "");

    var informDiv = document.getElementById("BrowserpedalsUiInformDiv");
    if (infoItems.length > 1) {
        informDiv.innerHTML = "";

        var select = document.createElement("SELECT");
        select.id = "BrowserpedalsUiInformSelect";
        select.className = "browserpedalsUiInformSelectClass";
        select.onchange = selectChanged;
        informDiv.appendChild(select);

        var infoArray = JSON.parse(infoItems);
        var i;
        for (i = 0; i < infoArray.length; i++) {
            var lang = infoArray[i][0];
            var langName = infoArray[i][1];

            var option = document.createElement("OPTION");
            option.className = "browserpedalsUiInformSelectOptionClass";
            option.value = lang;
            option.text = langName;
            select.add(option);

            if ((arguments.length > 3) && (lang == infoSelected)) {
                option.selected = true;
            }
        }
    } else {
        informDiv.innerHTML = infoString;
        informDiv.scrollTop = informDiv.scrollHeight;
    }

    var yesDiv = document.getElementById("BrowserpedalsUiYesDiv");
    if (yesName.length == 0) {
        yesDiv.style.visibility = "hidden";
    } else {
        yesDiv.style.visibility = "visible";
        var yesButton = document.getElementById("BrowserpedalsUiYesButton");
        yesButton.innerText = yesName;
    }

    var noDiv = document.getElementById("BrowserpedalsUiNoDiv");
    if (noName.length == 0) {
        noDiv.style.visibility = "hidden";
    } else {
        noDiv.style.visibility = "visible";
        var noButton = document.getElementById("BrowserpedalsUiNoButton");
        noButton.innerText = noName;
    }

    setupButtonsCallCount--;
}

setupButtons();

