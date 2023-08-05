const scannerDivId = "qr-reader";
const scannerDiv = $("div#" + scannerDivId);
const scanner = new Html5Qrcode(scannerDivId);

function onScanSuccess(decodedText, decodedResult) {
    let targetId = scannerDiv.data("target-input");
    let target = $("[name='" + targetId + "']");

    scanner.stop();

    target.val(decodedText);
    target.closest("form").submit();
}

$(document).ready(function($) {
    let cameraConfig = { facingMode: "environment" };
    let scannerConfig = { fps: 10, qrbox: {width: 250, height: 250} };

    scanner.start(cameraConfig, scannerConfig, onScanSuccess);
});
