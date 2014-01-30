$(function () {
	$("#select-btn").click(function () {
		$("#file-input").click();
	});

	$("#file-input").change(function () {
		var file = $(this)[0].files[0];

		if (!file.type.match(/image.*/)) {
			alert("This file is not image!");
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
		$("#upload-form").submit();
	});
});
