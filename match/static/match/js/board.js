$(document).ready(function() {
    let thrown_darts = [];

    $('.field').click(function () {
        if (thrown_darts.length < 3) {
            let val = $(this).data('value');
            let mult = $(this).data('multiplier');
            let score = $('.player.active').find('.score').text();
            thrown_darts.push(val * mult);
            score = score - (val * mult);
            $('.player.active').find('.score').text(score);
            $('.player.active').find(`#dart-${thrown_darts.length}`).text(val * mult);
        }
    });

    $('#next-player').click(function () {
        console.log(thrown_darts);
        // Send post request to save thrown darts and reload page with other player active?
    });

});