
$(window).load(function () {
    Stripe.setPublishableKey($('#codesy-html').data('stripe_key'));

    function response_div(message){
        $div= $(`
            <div class="callout warning expanded" data-closable>
                <button class="close-button" data-close>&times;</button>
                <p class="alert alert-error">
                </p>
            </div>`)
        $div.find('p').text(message)
        return $div
    }

    let stripeResponse = function (csrf_token) {
        function prepare_data ({type, id, card, bank_account }){
            switch (type) {
                case 'card':
                    ;( {last4: card_last4, brand: card_brand} = card)
                    return {stripe_card: id, card_last4, card_brand}
                    break;
                case 'bank_account':
                    return {stripe_bank_account: id}
                    break;
                default:
                    return {}
            }
        }

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
                    data: prepare_data(response),
                    success: (data, status, jqXHR) =>console.log("Updated user."),
                    error: (err) => console.error(err)
                });
            }
            $('#stripe-form').prepend(response_div(response_message))
            $('#stripe-submit').text('Submit Account Information');
        }
    }

    let handleResponse = new stripeResponse($('form input[name="csrfmiddlewaretoken"]').val())
    let $form = $('#stripe-form')
    let account_type = $form.attr('stripe-account-type')

    $('#codesy-submit').click(function (e) {
        // add account_holder_type for bank account and identity forms
        let holder_type = $("input[name=form_holder_type]:checked").val()
        if (holder_type) {
            $('#type').val(holder_type)
        }
    });

    $('#stripe-submit').click(function (e) {
        e.preventDefault();
        // add account_holder_type for bank account and identity forms
        let holder_type = $("input[name=form_holder_type]:checked").val()
        if (holder_type) {
            $('#account_holder_type').val(holder_type)
        }
        $('#stripe-submit').text('Submitting ... ');
        Stripe[account_type].createToken($form, handleResponse);
    });

})
