window.codesy={}
class WidgetApp {
    constructor($form) {
        this.$form = $form
        $form.submit(this.submit.bind(this))
        $form.find('button#ShowSubmit').click(this.show.bind(this))
        $form.find('input#cancelSubmit').click(this.reload.bind(this))
    }
    show(e) {
        e.preventDefault()
        $('.codesy_hide').hide()
        $('.codesy_confirm').removeClass('hide')
        var valid_ask = this.validate($("input#ask"))
        var valid_offer = this.validate($("input#offer"))
        if (valid_offer || valid_ask){
            this.$form.find('input[type="submit"]').removeClass('hide')
        }
    }
    validate($input){
        var original_value = $input.data("original-value")
        var new_value = $input.val()
        var diff = new_value - original_value
        var input_type = $input.attr('id')
        const $message = $(`<label id="${input_type}-confirm" class="callout small codesy_confirm" ></label>`)
        var validated = true
        var offer_notice = ''
        var direction = ''
        var introduction = ''

        this.$form.parent().prepend($message)

        if (new_value>0 && new_value<1){
            $message.text('Sorry, bids cannot be less than $1.')
            $input.val(original_value)
            return false
        }

        if (new_value<0){
            $message.text('Sorry, bids cannot be negative.')
            $input.val(original_value)
            return false
        }

        if (diff === 0){
            direction = 'not changing'
            validated = false
        }
        else if (diff > 0 ) {
            direction = `increasing`
        } else if (diff < 0) {
            direction = `decreasing`
        }

        introduction = `You are ${direction} your ${input_type}.`

        if (input_type === "offer"){
            if (diff < 0) {
                introduction =''
                offer_notice = "Sorry, you can't decrease your offer."
                $input.val(original_value)
                validated = false
            } else if (diff>0){
                offer_notice =`Your credit card will be authorized for $${new_value}.`
            }
        }
        $message.text([introduction,offer_notice].join(' '))
        return validated
    }
    submit(e){
        e.preventDefault()
        var form = this.$form
        var csrf_token = form.find('input[name=csrfmiddlewaretoken]').val()
        var api_call = $.ajax({
            url: form.attr('action'),
            method: form.attr("method"),
            data: form.serialize(),
            processData: false,
            headers: {
              'X-CSRFToken': csrf_token
            },
            contentType: 'application/x-www-form-urlencoded; charset=UTF-8'
            })
            .fail(function(data, textStatus, jqXHR) {
                $.each(data.responseJSON, function(key, value) {
                    this.error(value)
                });
            })
            .done(function(data, textStatus, jqXHR) {
                window.location.reload()
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
    codesy.app = new WidgetApp($('#codesy_form'))
});
