$(window).load(function () {
    Stripe.setPublishableKey($('#codesy-html').data('stripe_key'));
    stripeResponse = function (csrf_token) {
        this.csrf_token = csrf_token
        return (function(_this){
            return function (status, response) {
                if (response.error) {
                    console.error("Stripe failed to tokenize");
                    $('#payment-errors').text(response.error.message);
                    document.location.reload();
                } else {
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
                        },
                        complete: function(){
                            document.location.reload();
                        }
                    });
                }
            }
        })(this)
    }

    $('#stripe-submit').click(function (e) {
        e.preventDefault();
        $('#stripe-submit').text('Encrypting ... ');
        let $form = $('#stripe-form')
        let handleResponse = new stripeResponse($('form input[name="csrfmiddlewaretoken"]').val())
        let account_type = $form.attr('stripe-account-type')
        Stripe[account_type].createToken($form, handleResponse);
    });

})


// card.createToken
// bankAccount.createToken
