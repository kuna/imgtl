$(function () {
    $(".url-text").click(function() {
        $(this).select();
    });

    $("#delete-btn").click(function() {
        $('#delete-modal').modal({ show: true });
    });
    
    $("#delete-confirm-btn").click(function () {
        deleteImage(function () {
            location.href = '/';
        });
    });
    
    function deleteImage(cb) {
        $.ajax({
            type: 'DELETE',
            success: function(res) {
                if (res.res == 'success') {
                    showSuccess("이미지가 삭제되었습니다");
                } else if (res.res == 'nosuchimage') {
                    showError("존재하지 않는 이미지입니다");
                } else if (res.res == 'notmine') {
                    showError("자신의 이미지가 아닌 이미지는 삭제 할 수 없습니다");
                }
                
                if (typeof cb == 'function') { cb(); }
            }
        });
    }
});
