var latestTime = arguments[0];
var JUMP_BACK_SEC = arguments[1];

function jumpBack(vid) {
    if (vid && (vid.currentTime > JUMP_BACK_SEC)) {
        vid.currentTime -= JUMP_BACK_SEC;
    }
}

var timestamp = "0";
if (document.documentElement && document.documentElement.hasAttribute("data-last-manually-played-element-timestamp")) {
    timestamp = document.documentElement.getAttribute("data-last-manually-played-element-timestamp");
}

var frameLatestTime = Number(timestamp);
if (frameLatestTime > latestTime) {
    latestTime = frameLatestTime;
}
timestamp = latestTime.toString();

if (timestamp != "0") {
    elem = document.querySelector('[data-manually-played-element-timestamp="' + timestamp + '"]')
    if (elem) {
        jumpBack(elem);
    } else {
        timestamp = "0";
    }
}

return timestamp;

