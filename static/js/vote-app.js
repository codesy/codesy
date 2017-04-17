function make_submit_form (csrf_token){
    return function (e) {
        e.preventDefault();
        form = $(this)
        $.ajax( {
                url: form.attr('action'),
                method: form.data("method"),
                data: form.serialize(),
                processData: false,
                headers: {'X-CSRFToken': csrf_token},
                contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
                success: (data, textStatus, jqXHR) => window.location.reload(),
                error: console.error
            }
        );
    }
}

$(document).ready(function(){
    // start foundation js
    $(document).foundation();
    // set up generic ajax post to codesy
    const csrf_token_value = $('form input[name="csrfmiddlewaretoken"]').val()
    const submitForm = make_submit_form(csrf_token_value)
    $('form.vote-submit').submit(submitForm);
});
