function error_show() {
    $(".error").click(function () { error_hide(); });
    $(".overlay").click(function () { error_hide(); });
    setTimeout(function() { error_hide(); }, 3000);

    $(".error").animate({ top: "0" }, 800);
}

function error_hide() {
    $(".error").animate({ top: "-140px" }, 600);
    $(".overlay").animate({ opacity: "0" }, 600);
    setTimeout(function() {
        $(".overlay").remove();
    $(".error_parent").remove();
    }, 700);
}
