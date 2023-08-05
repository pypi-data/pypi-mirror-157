function getCheckpointCoords() {
    navigator.geolocation.getCurrentPosition(setCheckpointCoords);
}

function setCheckpointCoords(position) {
    $("[name='lat']").val(position.coords.latitude);
    $("[name='lon']").val(position.coords.longitude);

    window.setTimeout(function() {
        navigator.geolocation.getCurrentPosition(setCheckpointCoords);
    }, 3000);
}

$(document).ready(function($) {
    if (navigator.geolocation) {
        getCheckpointCoords();
    }
});
