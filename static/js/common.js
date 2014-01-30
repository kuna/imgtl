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
});
