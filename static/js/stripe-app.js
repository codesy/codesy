$(window).load(function () {
    Stripe.setPublishableKey($('#codesy-html').data('stripe_key'));
    let stripeResponse = function (csrf_token) {
        this.csrf_token = csrf_token
        return (function(_this){
            return function (status, response) {
                if (response.error) {
                    console.error("Stripe failed to tokenize");
                    message_array[3] = response.error.message
                } else {
                    message_array[3] = "Account Information successfully encrypted"
                    $.ajax({
                        method: "PATCH",
                        url: "/users/update/",
                        beforeSend: function(xhr, settings) {
                            xhr.setRequestHeader('X-CSRFToken', _this.csrf_token);
                        },
                        data: {['stripe_'+response.type]: response.id},
                        success: function(data, status, jqXHR) {
                            console.log("Updated user.");
                        },
                        error: function(err) {
                            console.error("Error updating user.");
                            console.error(err);
                        }
                    });
                }
                $('#stripe-form').prepend(message_array.join(""))
                $('#stripe-submit').text('Encrypt Account Information');
            }
        })(this)
    }

    let handleResponse = new stripeResponse($('form input[name="csrfmiddlewaretoken"]').val())
    let $form = $('#stripe-form')
    let account_type = $form.attr('stripe-account-type')
    let message_array = ['<div class="callout warning expanded" data-closable>',
        '<button class="close-button" data-close>&times;</button>',
        '<p class="alert alert-error">',
        'MESSSAGE GOES IN POS 3',
        '</p></div>']

    $('#stripe-submit').click(function (e) {
        e.preventDefault();

        // add account_holder_type for bank account and identity forms
        let holder_type = $("input[name=form_holder_type]:checked").val()
        if (holder_type) {
            $('#account_holder_type').val(holder_type)
        }
        $('#stripe-submit').text('Encrypting ... ');
        Stripe[account_type].createToken($form, handleResponse);
    });

})
