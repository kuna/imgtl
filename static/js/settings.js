$(function () {
	$("#token-modal-ok").click(function () {
		$.ajax({
			type: "POST",
			url: "/settings",
			data: "what=token",
			async: false,
			success: function (data) {
				if (data.token) {
					$("#t_token").val(data.token);
				}
				$("#token-modal").modal('hide')
			}
		});
	});
});
