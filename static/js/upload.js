$(function () {
	$("#select-btn").click(function () {
		$("#file-input").click();
	});

	$("#file-input").change(function () {
		var file = $(this)[0].files[0];

		if (!file.type.match(/image.*/)) {
			showError('이미지가 아닙니다.');
			return;
		}

		var path = $(this).val().split('\\');
		$("#filename-text").val(path[path.length - 1]);

		$("#upload-icon").css({
			"background-image": 'url(' + window.URL.createObjectURL(file) + ')',
			"background-size": "cover"
		});
	});

	$.event.props.push('dataTransfer');

	$("#upload-icon-frame").bind({
		click: function (e) {
			$("#file-input").click();
		},
		dragenter: function (e) {
			if (event.dataTransfer.dropEffect == "move") {
				event.preventDefault();
			}
		},
		dragover: function (e) {
			if (event.dataTransfer.dropEffect == "move") {
				event.preventDefault();
			}
		},
		drop: function (e) {
			e.stopPropagation();
			e.preventDefault();

			var file = event.dataTransfer.files[0];
			alert(file);
		}
	});

	$("#submit-btn").click(function () {
		exp = ($("#expire option:selected").val());
		if (exp != '-1') {
			if (exp == '0') {
				cst_exp = $("#expire-custom").val() * $("#expire-custom-unit").val();
				if (!(cst_exp > 0)) {
					showError("만료 시간을 정확히 입력해주세요.");
					return false;
				} else if (cst_exp > 518400) {
					showError("만료 시간은 1년을 넘을 수 없습니다.");
					return false;
				}
			}
		}
		$("#upload-form").submit();
	});
});
