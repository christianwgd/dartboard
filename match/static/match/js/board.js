function resetThrows() {
    $('.player.active').find('#dart-1').html(
        '<i class="far fa-long-arrow-alt-right"></i>'
    );
    $('.player.active').find('#dart-2').html(
        '<i class="far fa-long-arrow-alt-right"></i>'
    );
    $('.player.active').find('#dart-3').html(
        '<i class="far fa-long-arrow-alt-right"></i>'
    );
}


$(document).ready(function() {
    let thrown_darts = [];

    $('.field').click(function () {
        if (thrown_darts.length < 3) {
            let val = $(this).data('value');
            let mult = $(this).data('multiplier');
            let score = $('.player.active').find('.score').text();
            thrown_darts.push(val * mult);
            let check_score = score - (val * mult);
            if (check_score < 0) {
                alert("{% trans 'Busted' %}")
            } else {
                score = check_score;
                $('.player.active').find('.score').text(score);
                $('.player.active').find(`#dart-${thrown_darts.length}`).text(val * mult);
            }
        }
    });

    $('.undo').click(function() {
        if (thrown_darts.length > 0 && thrown_darts.length < 4) {
            let undo_score = 0;
            $('.player.active').find(`#dart-${thrown_darts.length}`).html(
            '<i class="far fa-long-arrow-alt-right"></i>'
            );
            undo_score = thrown_darts.pop();
            let score = parseInt($('.player.active').find('.score').text());
            score = score + undo_score;
            $('.player.active').find('.score').text(score);
        }
    });

    $('#next-player').click(function () {
        console.log(thrown_darts);
        if (thrown_darts.length < 3) {
            while (thrown_darts.length < 3) {
                thrown_darts.push(0);
            }
        }
        // Send post request to save thrown darts and reload page with other player active?
        let match_id = $('#match_id').text();
        let player_id = $('.player.active div div div div').attr('id');
        $.post({
            url: "/match/save_turn/"+match_id+"/",
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'player': player_id,
                'throw1': thrown_darts[0],
                'throw2': thrown_darts[1],
                'throw3': thrown_darts[2],
            },
            success: function(data) {
                let ret = JSON.parse(data);
                resetThrows();
                if (ret.success) {
                    $('.player.active').find('.old-score').html(ret.old_score);
                    $('.player.active').find('.throw-score').html(ret.throw_score);
                    if ($('.player.active').hasClass('player1')) {
                        $('.player1').removeClass('active');
                        $('.player2').addClass('active');
                    } else {
                        $('.player2').removeClass('active');
                        $('.player1').addClass('active');
                    }
                } else {
                    alert(ret.reason);
                }
             },
        });
        thrown_darts = [];
    });

});