var re_email = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
var re_username = /^[a-zA-Z0-9_]{4,16}$/;

$(function () {
    if (location.hash == "#register") {
        $(".login-form").hide();
        $(".register-form").show();
        $(".login-area").css("height", "585px");
    }
    
    $(window).on('hashchange', function () {
        if (location.hash == "#register") {
            $(".login-area").animate({
                height: "65px"
            }, 400, function () {
                $(".login-form").hide();
                $(".register-form").show();

                $(".login-area").animate({
                    height: "585px"
                }, 300);
            });
        } else if (location.hash == "#login") {
            $(".login-area").animate({
                height: "65px"
            }, 400, function () {
                $(".register-form").hide();
                $(".login-form").show();

                $(".login-area").animate({
                    height: "435px"
                }, 300);
            });
        }
    });
    
    // -- sign up value check event listener
    
    $("#inputREmail").change(function () {
        val = $(this).val();

        if (val.length > 120) {
            error($(this), "email address must be at most 120 characters long");
        } else if (!re_email.test(val)) {
            error($(this), "invalid email address");
        } else if (valueCheck(val, 'email', $(this).attr('except'))) {
            error($(this), "email address already exists");
        } else {
            ok($(this));
        }
    });

    $("#inputRUsername").change(function () {
        val = $(this).val();

        if (val.length < 4) {
            error($(this), "username must be at least 4 characters long");
        } else if (val.length > 16) {
            error($(this), "username must be at most 16 characters long");
        } else if (!re_username.test(val)) {
            error($(this), "username must contain only alphanumeric characters");
        } else if (valueCheck(val, 'username', $(this).attr('except'))) {
            error($(this), "username already exists");
        } else {
            ok($(this));
        }
    });


    $("#inputRPassword").keyup(function () {
        if ($(this).val().length < 8) {
            error($(this), "password must be least 8 characters");
        } else {
            ok($(this));
            $("#inputRPasswordConfirm").trigger("keyup");
        }
    });

    $("#inputRPasswordConfirm").keyup(function () {
        var $p = $(this).parent();

        if ($(this).val() != $("#inputRPassword").val()) {
            error($(this), "password did not match")
        } else {
            ok($(this));
        }
    });
});

function valueCheck(val, what, except) {
    res = false;
    data = "what=" + what + "&value=" + val;
    if (except !== undefined) data += '&except=' + except;
    $.ajax({
        type: "POST",
        url: "/signup/check",
        async: false,
        data: data,
        success: function (data) {
            res = data.res;
        }
    });
    return res;
}

function error($this, text) {
    var $p = $this.parent();
    $p.removeClass("success");
    $p.addClass("error");
    $p.children('.error-help').text(text).show();
    $('#register-submit-btn').attr('disabled', '');
}

function ok($this) {
    var $p = $this.parent();
    $p.children('.error-help').hide();
    $p.removeClass("error");
    $p.addClass("success");
    $('#register-submit-btn').removeAttr('disabled');
}
