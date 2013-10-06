function showError(msg) {
    showAlert("error-area", msg);
}

function showSuccess(msg) {
    showAlert("success-area", msg);
}

function showAlert(id, msg) {
    $("#" + id + " > #msg-text").text(msg);
    $("#" + id).animate({
        opacity: 1,
        top: 0
    }, 500);
    
    setTimeout(function () {
        $("#" + id).animate({
            opacity: 0,
            top: "-50"
        }, 500);
    }, 3000);
}

function showWhiteOverlay() {
    $(".white-overlay").css("display", "block");
    $(".white-overlay").animate({
        opacity: 0.7
    }, 500);
    
    setTimeout(function () {
        $(".white-overlay").animate({
            opacity: 0,
        }, 500, function () {
            $(".white-overlay").css("display", "none");
        });
    }, 3000);
}
