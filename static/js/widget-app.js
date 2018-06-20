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
    input_descriptor(input_type){
        let descriptor ="";
        switch (input_type) {
            case "offer":
                descriptor="fund"
                break;
            case "ask":
                descriptor="fix"
                break;
        }
        return descriptor
    }
    validate($input){
        var original_value = $input.data("original-value")
        var new_value = $input.val().replace('$', '');
        var diff = new_value - original_value
        var input_type = $input.attr('id')
        var validated = true
        var offer_notice = ''
        var direction = ''

        const $message = $(`<label id="${this.input_descriptor(input_type)}-confirm" class="callout small codesy_confirm" ></label>`)

        this.$form.parent().prepend($message)

        if (new_value>0 && new_value<1){
            $message.text(`Sorry, your ${this.input_descriptor(input_type)} amount cannot be less than $1.`)
            $input.val(original_value)
            return false
        }

        if (new_value<0){
            $message.text(`Sorry, your ${this.input_descriptor(input_type)} amount cannot be negative.`)
            $input.val(original_value)
            return false
        }

        if (diff === 0 || isNaN(diff)){
            direction = 'not changing'
            validated = false
        }
        else if (diff > 0 ) {
            direction = `increasing`
        } else if (diff < 0) {
            direction = `decreasing`
        }

        if (input_type === "offer"){
            if (diff < 0) {
                offer_notice = "Sorry, you can't decrease your funding."
                $input.val(original_value)
                validated = false
            } else if (diff>0){
                offer_notice =`Your credit card will be authorized for $${new_value}.`
            }
        }
        $message.text(`You are ${direction} your ${this.input_descriptor(input_type)} amount. ${offer_notice}`)

        return validated
    }
    submit(e){
        e.preventDefault()
        var form = this.$form
        form.find('input[type="submit"]').prop('value', "Submitting ...")
        form.find('input[type="submit"]').prop('disabled', true)
        var csrf_token = form.find('input[name=csrfmiddlewaretoken]').val()
        var api_call = $.ajax({
            url: form.attr('action'),
            method: form.attr("method"),
            data: form.serialize(),
            processData: false,
            headers: {'X-CSRFToken': csrf_token},
            contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
            success: window.location.reload.bind(window.location)
        })
        .fail(this.ajax_fail(this.$form))
    }
    reload() {
        window.location.reload()
    }
    ajax_fail($form) {
        function append(msg){
            let $div= $(`
                <div class="callout warning expanded" data-closable>
                    <button id="close-button" class="close-button" data-close>&times;</button>
                    <p class="alert"></p>
                </div>`)
            $div.find('p').text(msg)
            $form.parent().prepend($div)
        }
        return function (data, textStatus, jqXHR){
            data.responseJSON.evidence.forEach((e)=>append(e))
        }
    }
}//end class

$(document).ready(function() {
    codesy.app = new WidgetApp($('#codesy_form'))
});
