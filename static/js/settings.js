$(window).on('hashchange', function() {
    $(".settings-area > .content > div").hide();
    
    if (location.hash == "#account") {
        $("#account").show();
        $(".settings-area > .panel-heading > small").text("Account");
    } else if (location.hash == "#token") {
        $("#token").show();
        $(".settings-area > .panel-heading > small").text("Token");
    }
});

$(function () {
    if (location.hash == "#token") {
        $("#account").hide();
        $("#token").show();
        $(".settings-area > .panel-heading > small").text("Token");
    }
    
    $("#inputToken").click(function () {
        $(this).select();
    });
    
    $("#token-reissue-btn").click(function () {
        $.ajax({
            type: "POST",
            url: "/settings",
            data: "what=token",
            async: false,
            success: function (data) {
                if (data.token) {
                    $("#inputToken").val(data.token);
                }
                $("#token-modal").modal('hide')
            }
        });
    });
});
