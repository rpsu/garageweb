var holdReload = 0;
var reload_delay = 10;
var seconds = 0;

function refreshCheck() {
    if (seconds++ >= reload_delay && !holdReload) {
        seconds = 0; // We want to reset just to make sure the location reload is not called.
        window.location.reload(); // If this is called no reset is needed
    }
}
setInterval(function() {
    refreshCheck();
}, 1000);

function hold() {
    holdReload = true;
}

function release() {
    holdReload = false;
    seconds = 0;
}