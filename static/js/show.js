$(function () {
    $(".url-text").click(function() {
        $(this).select();
    });

    $("#delete-btn").click(function() {
        $.ajax({
            'type': 'DELETE',
            success: function(res) {
                if (res.res == 'success') {
                    alert("이미지가 삭제되었습니다");
                } else if (res.res == 'nosuchimage') {
                    alert("존재하지 않는 이미지입니다");
                } else if (res.res == 'notmine') {
                    alert("자신의 이미지가 아닌 이미지는 삭제 할 수 없습니다");
                } location.href = '/';
            }
        });
    });
});
