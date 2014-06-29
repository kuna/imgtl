$(function () {
	var grid = new freewall(".image-area")
	grid.reset({
		selector: '.grid-item',
		animate: true,
		cellW: 150,
		cellH: 150,
		onResize: function() {
			grid.fitWidth();
		}
	});
	grid.fitWidth();
	$(window).trigger("resize");

	$(".grid-item").mouseover(function () {
		$(this).animate({
			"border": "solid 1px rgba(49, 176, 213, 1)"
		}, 500);
	}).mouseout(function (){
		$(this).animate({
			"border": "solid 1px rgba(49, 176, 213, 0)"
		}, 500);
	});


	$("#show-nsfw").change(function() {
		if (this.checked) {
			$(".image-area > .nsfw").each(function() {
				$($(this).children("div")[0]).addClass('grid-item');
				$(this).show();
			});
			$(window).trigger("resize");
		} else {
			$(".image-area > .nsfw").each(function() {
				$($(this).children("div")[0]).removeClass('grid-item');
				$(this).hide();
			});
			$(window).trigger("resize");
		}
	});
	$("#show-nsfw").trigger("change");
});
