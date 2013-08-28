$(function () {
    $(".grid-item").mouseover(function () {
        $(this).animate({
            "border": "solid 1px rgba(49, 176, 213, 1)"
        }, 500);
    }).mouseout(function (){
        $(this).animate({
            "border": "solid 1px rgba(49, 176, 213, 0)"
        }, 500);
    });
});
