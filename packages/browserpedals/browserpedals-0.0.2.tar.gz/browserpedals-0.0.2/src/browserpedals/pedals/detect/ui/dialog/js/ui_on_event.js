var eventString = arguments[0];

function onEvent(eventStr) {
    var eventsDiv = document.getElementById("BrowserpedalsUiEventsDiv");
    eventsDiv.style.visibility = "visible";

    var eventText = document.createElement("DIV");
    eventText.className = "browserpedalsUiEventTextClass";

    var r = Math.floor((Math.random() * 180) + 10);
    var g = Math.floor((Math.random() * 180) + 10);
    var b = Math.floor((Math.random() * 180) + 10);
    eventText.style.color = "rgba(" + r +", " + g +", " + b +", 0.8)";

    eventText.innerHTML = eventStr;

    eventsDiv.appendChild(eventText);
    eventText.scrollIntoView(false);
}

onEvent(eventString);

