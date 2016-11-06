window.codesy={}
class WidgetApp {
    constructor($form) {
        this.$form = $form
        $form.find('input#submitForm').submit(this.submit.bind(this))
        $form.find('button#ShowSubmit').click(this.show.bind(this))
        $form.find('button#cancelSubmit').click(this.reload.bind(this))
    }
    show(e) {
        e.preventDefault()
        var valid_offer = this.validate($("input#offer"))
        var valid_ask = this.validate($("input#ask"))
        if (valid_offer || valid_ask){
            this.$form.find('#submitForm').removeClass('hide')
        }
        $('.codesy_hide').hide()
        $('.codesy_confirm').removeClass('hide')
    }
    validate($input){
        var original_value = $input.data("original-value")
        var new_value = $input.val()
        var diff = new_value - original_value
        const $message = $('<label id="ask-confirm" class="callout small codesy_confirm hide" ></label>')
        var validated = true
        var offer_notice = ''
        var direction = ''
        var input_type = $input.attr('id')

        if (diff === 0){
            direction = 'did not change.'
            validated = false
        }
        else if (diff > 0 ) {
            direction = `is increasing to $${new_value}`
        } else if (diff < 0) {
            direction = `is decreasing to $${new_value}`
        }

        let introduction = `Your ${input_type} ${direction}.`

        if (input_type === "offer"){
            if (diff < 0) {
                introduction =''
                offer_notice = "Sorry, you can't decrease your offer."
                $input.val(original_value)
                validated = false
            } else if (diff>0){
                offer_notice =`
                    This ${ original_value === "" || original_value === 0 ? "new" : ""}
                    offer will be authorized on your credit card
                `
            }
        }
        $message.text([introduction,offer_notice].join(' '))
        this.$form.prepend($message)
        return validated
    }
    submit(e){
        e.preventDefault()
        var form = this.$form
        var csrf_token = form.find('input[name=csrfmiddlewaretoken]').val()
        var api_call = $.ajax({
            url: form.attr('action'),
            method: form.data("method"),
            data: form.serialize(),
            processData: false,
            headers: {
              'X-CSRFToken': csrf_token
            },
            contentType: 'application/x-www-form-urlencoded; charset=UTF-8'
            })
            .error(function(data, textStatus, jqXHR) {
                $.each(data.responseJSON, function(key, value) {
                    this.error(value)
                });
            })
            .done(function(data, textStatus, jqXHR) {
                this.reload()
            })
    }
    reload() {
        window.location.reload()
    }
    error(message){
        $div= $(`
            <div class="callout warning expanded" data-closable>
                <button class="close-button" data-close>&times;</button>
                <p class="alert alert-error">
                </p>
            </div>`)
        $div.find('p').text(message)
        return $div
    }
}//end class

$(document).ready(function() {
    codesy.app = new WidgetApp($('#codesy_bid'))
});
