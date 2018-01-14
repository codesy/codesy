// create codesy object for ga analytics
window.codesy = {};

$(window).on("load",function () {
    // start foundation js
    $(document).foundation();

    const csrf_token_value = $('form input[name="csrfmiddlewaretoken"]').val()

    function response_div(message){
        $div= $(`<div id="stripe-response" class="callout warning expanded" data-closable>
                    <button class="close-button" data-close>&times;</button>
                    <p class="alert alert-error"></p>
                </div>`)
        $div.find('p').text(message)
        return $div
    }

    function make_submit (csrf_token){
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

    function stripe_to_codesy (account_type){
        // returns a function to read stripe response and return update parameters
        // for codesy based on what type of account is being updated
        switch (account_type) {
            case 'card':
                return ({ id, card: {last4: card_last4 , brand: card_brand} }) => {
                    return {stripe_card: id, card_last4, card_brand};
                }
                break;
            case 'bankAccount':
                return ({id: stripe_bank_account}) => {return {stripe_bank_account}};
                break;
            default:
                return ()=>{}
        };
    }

    function stripeResponse (csrf_token, get_parameters) {
        redirect = (url) => {window.location = url};
        const return_url = $('#return_url').val()
        const button_text = $('#stripe-submit').text()
        const success_msg = "Account information successfully submitted"
        const redirect_url = "/"

        function complete_submit (message) {
            $('#stripe-response').remove();
            $('#stripe-form').prepend(response_div(message));
            $('#stripe-submit').text(button_text);
        }

        function ajax_before (xhr, settings) {
            xhr.setRequestHeader('X-CSRFToken', csrf_token)
        }

        function ajax_success (data, status, jqXHR) {
            console.log("Updated user.");
            if ( return_url ) {
                redirect(return_url)
            } else {
                complete_submit(success_msg)
                redirect(redirect_url)
            };
        }

        function ajax_error (jqXHR, textStatus, errorThrown){
            console.error(errorThrown, textStatus)
            complete_submit(textStatus)
        }
        //receives the results of Stripe.createToken and updates codesy database
        return function (status, response){
            if (response.error) {
                console.error(`Stripe failed to tokenize: ${response.error.message}`);
                complete_submit(response.error.message)
            } else {
                $.ajax({
                    method: "PATCH",
                    url: "/users/update/",
                    beforeSend: ajax_before,
                    data: get_parameters(response),
                    success: ajax_success,
                    error: ajax_error
                })
            }
        }
    }

    function set_holder_type($element) {
        const holder_type = $("input[name=form_holder_type]:checked").val()
        if (holder_type) $element.val(holder_type)
    }

// load stripe form
    const $stripe_form = $('#stripe-form')
    $($stripe_form).ready( () => {
        Stripe.setPublishableKey($('#codesy-html').data('stripe_key'));
        const stripe_account_type = $stripe_form .attr('stripe-account-type')
        const get_parameters = stripe_to_codesy(stripe_account_type)
        const handleResponse = new stripeResponse(csrf_token_value, get_parameters)

        $('#stripe-submit').click(function (e) {
            e.preventDefault();
            set_holder_type($('#account_holder_type'))
            $('#stripe-submit').text('Submitting ... ');
            Stripe[stripe_account_type].createToken($stripe_form, handleResponse);
        });
    })

// EVENTS
    $('.popup').click(function(e) {
      var url = this.href;
      window.open(url, 'Share', 'status=1,left=0,top=0,width=575,height=400');
      return false;
    });

    $('form.vote-submit').submit( make_submit(csrf_token_value) );

    $('#codesy-submit-identity').click( (e)=> set_holder_type($('#type')) );

    // remove any notification divs when any modal form closes
    $(window).on('closed.zf.reveal', ()=>{
        $('#stripe-response').remove();
        window.location.reload();
    });
})
