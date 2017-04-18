function response_div(message){
    $div= $(`<div id="stripe-response" class="callout warning expanded" data-closable>
                <button class="close-button" data-close>&times;</button>
                <p class="alert alert-error"></p>
            </div>`)
    $div.find('p').text(message)
    return $div
}
// remove any notification divs when any modal form closes
$(window).on('closed.zf.reveal', ()=>$('#stripe-response').remove());

function make_codesy_submitter (account_type){
    switch (account_type) {
        case 'card':
            return ({ id, card: {last4, brand} }) => ({stripe_card: id, card_last4: last4, card_brand: brand});
            break;
        case 'bankAccount':
            return ({id}) => ({stripe_bank_account: id});
            break;
        default:
            return ()=>{}
    };
}

function stripeResponse (csrf_token, type) {
    const codesy_data = make_codesy_submitter(type)
    return function (status, response) {
        if (response.error) {
            console.error(`Stripe failed to tokenize: ${response.error.message}`);
            response_message = response.error.message
        } else {
            response_message = "Account information successfully submitted"
            $.ajax({
                method: "PATCH",
                url: "/users/update/",
                beforeSend: (xhr, settings) => xhr.setRequestHeader('X-CSRFToken', csrf_token),
                data: codesy_data(response),
                success: (data, status, jqXHR) => console.log("Updated user."),
                error: console.error
            });
        }
        $('#stripe-response').remove()
        $('#stripe-form').prepend(response_div(response_message))
        $('#stripe-submit').text('Submit Account Information');
    }
}

function set_holder_type($element) {
    const holder_type = $("input[name=form_holder_type]:checked").val()
    if (holder_type) $element.val(holder_type)
}

$(window).load(function () {
    Stripe.setPublishableKey($('#codesy-html').data('stripe_key'));
    const $form = $('#stripe-form')
    const stripe_account_type = $form.attr('stripe-account-type')
    const csrf_token_value = $form.find('input[name="csrfmiddlewaretoken"]').val()
    const handleResponse = new stripeResponse(csrf_token_value, stripe_account_type)

    $('#codesy-submit-identity').click( (e)=> set_holder_type($('#type')) );

    $('#stripe-submit').click(function (e) {
        e.preventDefault();
        set_holder_type($('#account_holder_type'))
        $('#stripe-submit').text('Submitting ... ');
        Stripe[stripe_account_type].createToken($form, handleResponse);
    });
})
