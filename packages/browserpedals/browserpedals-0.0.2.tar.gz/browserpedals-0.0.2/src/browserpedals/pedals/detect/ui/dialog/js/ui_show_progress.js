var val = arguments[0];
var maxVal = arguments[1];
var msgStr = arguments[2];

function showProgress(value, maximum, infoStr) {
    var progressDiv = document.getElementById("BrowserpedalsUiProgressDiv");
    if (value < 0) {
        progressDiv.style.visibility = "hidden";

        var informDiv = document.getElementById("BrowserpedalsUiInformDiv");
        informDiv.innerHTML = "";

        return
    }
    progressDiv.style.visibility = "visible";

    var percent = Math.round((value / maximum) * 100);
    var percentStr = percent.toString() + "%";
    var minusPercentStr = "-" + percentStr;
    var round_value = Math.round(value)
    var textStr = round_value.toString() + " of " + maximum.toString() + " sec";

    var progressVal = document.getElementById("BrowserpedalsUiProgressVal");
    progressVal.style.width = percentStr; // set progress value

    var progressText = document.getElementById("BrowserpedalsUiProgressText");
    progressText.style.margin = minusPercentStr; // set to minus progress value
    progressText.innerHTML = textStr; // set progress value as text

    if (infoStr.length > 0) {
        var informDiv = document.getElementById("BrowserpedalsUiInformDiv");
        informDiv.innerHTML = infoStr;
        informDiv.scrollTop = informDiv.scrollHeight;

        var yesDiv = document.getElementById("BrowserpedalsUiYesDiv");
        yesDiv.style.visibility = "hidden";

        var noDiv = document.getElementById("BrowserpedalsUiNoDiv");
        noDiv.style.visibility = "hidden";

        var eventsDiv = document.getElementById("BrowserpedalsUiEventsDiv");
        while (eventsDiv.hasChildNodes()) {  
            eventsDiv.removeChild(eventsDiv.firstChild);
        }
    }
}

showProgress(val, maxVal, msgStr);

