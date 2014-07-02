$(function () {
	$("#delete-modal-ok").click(function () {
		$("#delete-modal").modal('hide');
		$.ajax({
			type: 'DELETE',
			success: function(res) {
				if (res.res === 'nosuchimage') {
					showError("존재하지 않는 이미지입니다.");
				} else if (res.res === 'notmine') {
					showError("자신의 이미지가 아닌 이미지는 삭제 할 수 없습니다.");
				} else if (res.res === 'success') {
					location.href = '/';
				}
			}
		});
	});

	$("#update-submit-btn").click(function () {
		$.ajax({
			type: 'PUT',
			data: {'nsfw': $("input:checkbox[name='nsfw']").is(":checked"),
					'anonymous': $("input:checkbox[name='anonymous']").is(":checked"),
					'private': $("input:checkbox[name='private']").is(":checked")
					},
			success: function(res) {
				if (res.res === 'success') {
					showSuccess("설정을 저장하였습니다.");
				} else if (res.res === 'nosuchimage') {
					showError("존재하지 않는 이미지입니다.");
				} else if (res.res === 'notmine') {
					showError("자신의 이미지가 아닌 이미지의 설정은 바꿀 수 없습니다.");
				}
			}
		});
	});

	$("#nsfw-modal-ok").click(function() {
		$(".image").removeClass("nsfw");
		$(".image").css("visibility", "visible");
		$(".canvas").remove();
		$("#nsfw-modal").modal("hide");
	});

	$("#nsfw-modal").on('hide.bs.modal', function() {
		if ($(".image").hasClass("nsfw")) {
			$(".contents > .panel-body").css('visibility', 'hidden');
			showError("이미지를 표시하지 않습니다.");
		}
	});

	if ((/MSIE (\d+\.\d+);/.test(navigator.userAgent) && Number(RegExp.$1) >= 10.0) || !!navigator.userAgent.match(/Trident.*rv[ :]*11\./)) {
		if ($(".image").hasClass("nsfw")) {
			$(".image").css("visibility", "hidden");
			$(".contents").load(function() {
				$(".contents > .panel-body").append('<div class="canvas"><canvas id="blur-canvas"></canvas></div>');
				integralBlurImage( 'image', 'blur-canvas', 200, false, 1 );
				$(".canvas").offset($(".image").offset());
				$(".canvas").width($(".image").width()).height($(".image").height());
				$("#blur-canvas").width($(".image").width()).height($(".image").height());
			});
		}
	}
});
