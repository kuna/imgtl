var lastid = null;
var timeoutobj = null;

function showError(msg) {
	showAlert("error-area", msg);
}

function showSuccess(msg) {
	showAlert("success-area", msg);
}

function showAlert(id, msg) {
	showWhiteOverlay();
	$("#" + id + " > #msg-text").text(msg);
	$("#" + id).animate({
		opacity: 1,
		top: 0
	}, 500);

	lastid = id;
	setTimeout(hideAlertAndWhiteOverlay, 2000);
}

function hideAlert() {
	$("#" + lastid).animate({
		opacity: 0,
		top: "-50"
	}, 500);
}

function showWhiteOverlay() {
	$(".white-overlay").css("display", "block");
	$(".white-overlay").animate({
		opacity: 0.7
	}, 500);
}

function hideWhiteOverlay() {
	$(".white-overlay").animate({
		opacity: 0,
	}, 500, function () {
		$(".white-overlay").css("display", "none");
	});
}

function hideAlertAndWhiteOverlay() {
	hideAlert();
	hideWhiteOverlay();
}

$(function() {
	$(".white-overlay, .alert-area").click(function() {
		clearTimeout(timeoutobj);
		hideAlertAndWhiteOverlay();
	});

	$("select").not('.input-lg').not('.input-sm').each(function() {
		var e = $(this)
			e.select2({
			minimumResultsForSearch: 25565,
		})
	});

	$("#expire").change(function() {
		var val = $("#expire option:selected").val()
		if (val != '-1') {
			$("#expire-behavior-wrap").removeClass('hidden');
			if (val == '0')
				$("#expire-custom-wrap").removeClass('hidden');
			else
				$("#expire-custom-wrap").addClass('hidden');
		} else {
			$("#expire-custom-wrap").addClass('hidden');
			$("#expire-behavior-wrap").addClass('hidden');
		}
	});

	$("#expire-custom-unitdd > li > a").click(function() {
		$("#expire-custom-unit").val($(this).attr('data-value'));
		$("#expire-custom-unit-text").text($(this).text());
	});

	$("#expire-custom").keypress(function(e) {
		var charCode = (e.which) ? e.which : event.keyCode
		if (charCode > 31 && (charCode < 48 || charCode > 57))
			return false;
		return true;
	});
});
