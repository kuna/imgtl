var re_email = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
var re_username = /^[a-zA-Z0-9_]{4,16}$/;

$(function () {
	if (location.hash == "#signup") {
		$(".login-form").hide();
		$(".signup-form").show();
		$(".login-area").css("height", "585px");
	}

	$(window).on('hashchange', function () {
		if (location.hash == "#signup") {
			$(".login-area").animate({
				height: "65px"
			}, 400, function () {
				$(".login-form").hide();
				$(".signup-form").show();

				$(".login-area").animate({
					height: "585px"
				}, 300);
			});
		} else if (location.hash == "#login") {
			$(".login-area").animate({
				height: "65px"
			}, 400, function () {
				$(".signup-form").hide();
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
			error($(this), "이메일 길이는 120자를 넘을 수 없습니다");
		} else if (!re_email.test(val)) {
			error($(this), "잘못된 이메일 주소입니다");
		} else if (valueCheck(val, 'email', $(this).attr('except'))) {
			error($(this), "이미 사용중인 이메일 주소입니다");
		} else {
			ok($(this));
		}
	});

	$("#inputRUsername").change(function () {
		val = $(this).val();

		if (val.length < 4) {
			error($(this), "사용자명은 최소 4자 이상이어야 합니다");
		} else if (val.length > 16) {
			error($(this), "사용자명은 16자를 넘을 수 없습니다");
		} else if (!re_username.test(val)) {
			error($(this), "사용자명에는 숫자, 알파벳, _ 기호만이 사용 가능합니다");
		} else if (valueCheck(val, 'username', $(this).attr('except'))) {
			error($(this), "이미 사용중인 사용자명입니다");
		} else {
			ok($(this));
		}
	});


	$("#inputRPassword").keyup(function () {
		if ($(this).val().length < 8) {
			error($(this), "비밀번호는 최소 8자 이상이어야 합니다");
		} else {
			ok($(this));
			$("#inputRPasswordConfirm").trigger("keyup");
		}
	});

	$("#inputRPasswordConfirm").keyup(function () {
		var $p = $(this).parent();

		if ($(this).val() != $("#inputRPassword").val()) {
			error($(this), "비밀번호가 일치하지 않습니다")
		} else {
			ok($(this));
		}
	});
});

function valueCheck(val, what, except) {
	if (val == except) return false;
	res = false;
	$.ajax({
		type: "POST",
		url: "/signup/check",
		async: false,
		data: "what=" + what + "&value=" + val,
		success: function (data) {
			res = data.res;
		}
	});
	return res;
}

function error($this, text) {
	var $p = $this.parent();
	$p.removeClass("has-success");
	$p.addClass("has-error");
	$p.children('.error-help').text(text).show();
	$('#signup-submit-btn').attr('disabled', 'disabled');
}

function ok($this) {
	var $p = $this.parent();
	$p.children('.error-help').hide();
	$p.removeClass("has-error");
	$p.addClass("has-success");
	var flag = true;
	$(".signup-form > div.form-group").each(function () {
		if ($(this).hasClass('has-error'))
			flag = false;
	});
	if (flag) $('#signup-submit-btn').removeAttr('disabled');
}
