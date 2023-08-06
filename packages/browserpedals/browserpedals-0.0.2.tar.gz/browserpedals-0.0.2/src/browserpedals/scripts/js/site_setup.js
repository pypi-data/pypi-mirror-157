if (!document.documentElement)
    return;

if (!document.body)
    return;

document.documentElement.setAttribute("data-last-manually-played-element-timestamp", "0");

document.documentElement.setAttribute("data-tab-recent-visibility-timestamps", "");

const VISIBILITY_POLL_PERIOD_MILLISEC = 1500;
const MAX_TIMESTAMPS_COUNT = 5;


// User starts controlling a video/audio by clicking "Play":
document.addEventListener('play', function(e) {
    e = e || window.event;
    var elem = e.target || e.srcElement;

    var timestamp = Date.now().toString();
    elem.setAttribute("data-manually-played-element-timestamp", timestamp);

    document.documentElement.setAttribute("data-last-manually-played-element-timestamp", timestamp);
}, true);

// User stops controlling a video/audio by clicking anywhere on the video/audio iframe:
document.addEventListener('click', function(e) {
    e = e || window.event;
    var elem = e.target || e.srcElement;

    elem.removeAttribute("data-manually-played-element-timestamp");

    document.documentElement.setAttribute("data-last-manually-played-element-timestamp", "0");
}, false);

// audio/video has reached the end:
document.addEventListener('ended', function(e) {
    e = e || window.event;
    var elem = e.target || e.srcElement;

    elem.removeAttribute("data-manually-played-element-timestamp");

    document.documentElement.setAttribute("data-last-manually-played-element-timestamp", "0");
}, true);


// Record the recent times when user selected this tab:

const recentVisibilityTimestamps = [];
var lastTimestampIndex = -1;

function recordTabVisibility() {
    var testTime = Date.now();
    var tabVisibility = document.visibilityState;

    lastTimestampIndex++;
    if (lastTimestampIndex >= MAX_TIMESTAMPS_COUNT) {
        lastTimestampIndex = 0;
    }

    const timestamp = {};
    timestamp["test_time"] = testTime;
    timestamp["tab_visibility"] = tabVisibility;
    recentVisibilityTimestamps[lastTimestampIndex] = timestamp;

    const obj = {};
    obj["recent_visibility_timestamps"] = recentVisibilityTimestamps;
    obj["last_timestamp_index"] = lastTimestampIndex;
    var dataStr = JSON.stringify(obj);

    document.documentElement.setAttribute("data-tab-recent-visibility-timestamps", dataStr);
}

setInterval(recordTabVisibility, VISIBILITY_POLL_PERIOD_MILLISEC);


// Control out-of-DOM audios:

Audio.prototype.overwrite_play = Audio.prototype.play;

const MAX_CONNECTED_PLAY_COUNT = 10;
var connectedPlayCount = 0;

Audio.prototype.play = function() {
    if (!this.isConnected) {
        document.body.appendChild(this);

        Audio.prototype.play = Audio.prototype.overwrite_play;
    } else {
        connectedPlayCount++;
        if (connectedPlayCount > MAX_CONNECTED_PLAY_COUNT) {
            Audio.prototype.play = Audio.prototype.overwrite_play;
            this.play = Audio.prototype.overwrite_play;
        }
    }

    return this.overwrite_play(arguments);
}

