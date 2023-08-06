var latestTime = arguments[0];

function pausePlay(vid) {
    if (vid) {
        if (vid.paused || vid.ended) {
            vid.play();
        } else {
            vid.pause();
        }
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
        pausePlay(elem);
    } else {
        timestamp = "0";
    }
}

return timestamp;

