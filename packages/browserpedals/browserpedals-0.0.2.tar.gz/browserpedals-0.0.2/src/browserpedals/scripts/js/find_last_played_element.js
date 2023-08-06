var timestamp = "none";
if (document.documentElement && document.documentElement.hasAttribute("data-last-manually-played-element-timestamp")) {
    timestamp = document.documentElement.getAttribute("data-last-manually-played-element-timestamp");
}

return timestamp;

