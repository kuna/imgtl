$(function () {
    showError();
    setTimeout(hideError, 4000);

    $("#error-alert").click(hideError);
    $("#error-overlay").click(hideError);
});

function showError() {
    $("#error-alert").animate({
        'top': '0'
    }, 1000);

    $("#error-overlay").animate({
        'opacity': '0.5'
    }, 1000);
}

function hideError() {
    $("#error-alert").animate({
        'top': '-100px'
    }, 1000);

    $("#error-overlay").animate({
        'opacity': '0'
    }, 1000, function () {
        $(this).hide();
        $("#error-wrap").remove();
    });
}
