$(function () {
	$(".tool-tip").each(function () {
		$(this).tooltip({
			container: 'body',
		});
	});

	$(".url-text").click(function() {
		$(this).select();
	});

	$("#delete-confirm-btn").click(function () {
		$("#delete-modal").modal('hide');
		deleteImage(function () {
			location.href = '/';
		});
	});

	$("#update-submit-btn").click(function () {
		updateImage();
	});

	function deleteImage(cb) {
		$.ajax({
			type: 'DELETE',
			success: function(res) {
				if (res.res == 'nosuchimage') {
					showError("존재하지 않는 이미지입니다");
				} else if (res.res == 'notmine') {
					showError("자신의 이미지가 아닌 이미지는 삭제 할 수 없습니다");
				} else if (res.res == 'success') {
					if (typeof cb == 'function') { cb(); }
				}
			}
		});
	}

	function updateImage() {
		$.ajax({
			type: 'PUT',
			data: {'nsfw': $("input:checkbox[name='nsfw']").is(":checked"),
					'anonymous': $("input:checkbox[name='anonymous']").is(":checked"),
					'private': $("input:checkbox[name='private']").is(":checked"),
					},
			success: function(res) {
				if (res.res == 'success') {
					showSuccess("설정을 저장하였습니다");
				} else if (res.res == 'nosuchimage') {
					showError("존재하지 않는 이미지입니다");
				} else if (res.res == 'notmine') {
					showError("자신의 이미지가 아닌 이미지의 설정은 바꿀 수 없습니다");
				}
			}
		});
	}

	$("#shownsfw-confirm-btn").click(function() {
		$(".content-image").removeClass("nsfw");
		$("#nsfw-modal").modal("hide");
	});

	$("#nsfw-modal").on('hide.bs.modal', function(e) {
		if ($(".content-image").hasClass("nsfw")) {
			$(".content-image").css('visibility', 'hidden');
			showError("이미지를 표시하지 않습니다");
		}
	});

});
