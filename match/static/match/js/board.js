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

const animateCSS = (node, animation, prefix = 'animate__') =>
  // We create a Promise and return it
  new Promise((resolve, reject) => {
    const animationName = `${prefix}${animation}`;
    //const node = document.querySelector(element);

    node.classList.add(`${prefix}animated`, animationName);

    // When the animation ends, we clean the classes and resolve the Promise
    function handleAnimationEnd(event) {
      event.stopPropagation();
      node.classList.remove(`${prefix}animated`, animationName);
      resolve('Animation ended');
    }

    node.addEventListener('animationend', handleAnimationEnd, {once: true});
});

function update_checkout_way() {
    let remaining = parseInt($('.player.active').find('.score').text());
    $.get({
        url: `/match/checkout/${remaining}/`,
        crossDomain: true,
        contentType: "application/json",
        success: function (response) {
            if (response == null) return;
            $('.player.active').find('.suggestion').css('visibility', 'visible')
            let darts = response["darts"];
            let i = 1;
            for (let dart of darts) {
                $('.player.active').find(`#dart-${i}-suggestion`).text(`${dart.region.charAt(0)}${dart.field}`);
                i++;
            }
            // Only 2 darts needed for checkout
            if (i < 4) {
                $('.player.active').find('#dart-3-suggestion').text('');
            }
            // Only 1 dart needed for checkout
            if (i < 3) {
                $('.player.active').find('#dart-2-suggestion').text('');
            }
        },
        error: function (xhr, status) {
            console.log(xhr, status);
            alert("error");
        }
    });
}


$(document).ready(function() {
    let win_leg_modal = new bootstrap.Modal($('#leg-win-modal'));
    let thrown_darts = [];
    $('.'+set_active).addClass('active');
    update_checkout_way();
    let double_out = $('#out-type').text() === "Double Out";
    $('.field').click(function () {
        if (thrown_darts.length < 3) {
            let val = $(this).data('value');
            let mult = $(this).data('multiplier');
            let $score_el = $('.player.active').find('.score');
            let score = $score_el.text();
            thrown_darts.push(val * mult);
            let check_score = score - (val * mult);
            // 1 or below 0 is busted
            // 0 -> Check if out according to game outage
            if (check_score === 0 && (!double_out || mult === 2)) {
                let player_name = $('.player.active').find('.player-name').text().trim();
                $('.player.active').find('.score').text(check_score);
                $('#winner').text(player_name);
                win_leg_modal.show();
            } else if (check_score <= 1)  {
                $score_el.addClass('animate__animated animate__backOutDown');
                setTimeout(function () {
                    $score_el.removeClass('animate__animated animate__backOutDown');
                    $score_el.text($('.player.active').find('.score').text());
                    $score_el.addClass('animate__animated animate__backInDown');
                }, 1000)
            } else {
                score = check_score;
                $('.player.active').find('.score').text(score);
                $('.player.active').find(`#dart-${thrown_darts.length}`).text(val * mult);
            }
            update_checkout_way();
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
            update_checkout_way();
        }
    });

    $('#next-player, #next-leg').click(function () {
        let pressed_button = $(this);
        if (thrown_darts.length < 3) {
            while (thrown_darts.length < 3) {
                thrown_darts.push(0);
            }
        }
        // Send post request to save thrown darts and reload page with other player active?
        let match_id = $('#match_id').text();
        let player_id = $('.player.active div div div div').attr('id');
        $.post({
            url: `/match/save_turn/${match_id}/`,
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'player': player_id,
                'throw1': thrown_darts[0],
                'throw2': thrown_darts[1],
                'throw3': thrown_darts[2],
                'won': pressed_button.attr('id') === 'next-leg',
            },
            success: function(data) {
                resetThrows();
                if (data.success) {
                    if (pressed_button.attr('id') === 'next-leg') {
                        win_leg_modal.hide();
                        console.log(data.next_player);
                        next_leg(data.next_player);
                        return
                    }
                    $('.player.active').find('.old-score').html(data.old_score);
                    $('.player.active').find('.throw-score').html(data.throw_score);
                    if ($('.player.active').hasClass('player1')) {
                        $('.player1').removeClass('active');
                        $('.player2').addClass('active');
                    } else {
                        $('.player2').removeClass('active');
                        $('.player1').addClass('active');
                    }
                } else {
                    alert(data.reason);
                }
                update_checkout_way();
             },
        });
        thrown_darts = [];
    });

});

function next_leg(starting_player) {
    if (starting_player === 1) {
        $('.player2').removeClass('active');
        $('.player1').addClass('active');
    } else if (starting_player === 2){
        $('.player1').removeClass('active');
        $('.player2').addClass('active');
    } else {
        alert("received wrong argument when starting next leg")
    }
    $('.score').each(function() {
        $(this).text($('.match-type').text().trim());
    })
    $('.suggestion').each(function() {
        $(this).css('visibility', 'hidden');
    })
    $('.old-score').each(function() {
        $(this).text('');
    })
    $('.throw-score').each(function() {
        $(this).text('');
    })
}