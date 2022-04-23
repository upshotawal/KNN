$(document).ready(function() {
    $("#Genre-filter").on('click', function() {
        var x = this.value;
        console.log('You selected: ', x);
        $.ajax({
            url: "/filter",
            data: {
                x: x
            },
            datatype: 'json',

            success: function(res) {
                console.log("success");
                $("#unique").html(res.data)
            }
        });
    });
    // Get all <audio> elements.
    const audios = document.querySelectorAll('audio');

    // Pause all <audio> elements except for the one that started playing.
    function pauseOtherAudios({ target }) {
        for (const audio of audios) {
            if (audio !== target) {
                audio.pause();
            }
        }
    }

    // Listen for the 'play' event on all the <audio> elements.
    for (const audio of audios) {
        audio.addEventListener('play', pauseOtherAudios);
    }


    $('.like-form').submit(function(e) {
        e.preventDefault()

        const blog_id = $(this).attr('id')

        const likeText = $(`.like-btn${blog_id}`).text()
        const trim = $.trim(likeText)

        const url = $(this).attr('action')

        let res;
        const likes = $(`.like-count${blog_id}`).text()
        const trimCount = parseInt(likes)

        $.ajax({
            type: 'blog',
            url: url,
            data: {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                'blog_id': blog_id,
            },
            success: function(response) {
                if (trim === 'Unlike') {
                    $(`.like-btn${blog_id}`).text('Like')
                    res = trimCount - 1
                } else {
                    $(`.like-btn${blog_id}`).text('Unlike')
                    res = trimCount + 1
                }

                $(`.like-count${blog_id}`).text(res)
            },
            error: function(response) {
                console.log('error', response)
            }
        })

    })

});