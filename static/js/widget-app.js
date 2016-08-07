window.codesy = {
};

function submitForm(e) {
  e.preventDefault();
  form = $(this)
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

  });

  api_call.always(function(data, textStatus, jqXHR) {
    window.location.reload()
  })

}

// TODO: foo these functions out of the global scope
labelDiff = function(type, $from_elem, $to_elem){
    var original_value = $from_elem.data("original-value")
    var new_value = $from_elem.val()
    var diff = new_value - original_value
    var confirmTemplate =[]

    if (type === "ask"){
        if (diff === 0 ){
            confirmTemplate=["Your ask did not change"]
        } else if (diff > 0 ) {
            confirmTemplate = ["Your ask is increasing to ",new_value]
        } else if (diff < 0) {
            confirmTemplate = ["Your ask is decreasing to ",new_value]
        }
    }

    if (type === "offer"){
        if (diff === 0 ){
            confirmTemplate=["Your offer did not change."]
        } else if (diff > 0 ) {
            confirmTemplate = ["Your offer increased. $",diff," will be authorized your credit card."]
        } else if (diff < 0) {
            confirmTemplate = ["Sorry, you can't decrease your offer."]
            $from_elem.val(original_value)
        }
    }

    $to_elem.text(confirmTemplate.join(""))
}


function reloadPlease(){
    window.location.reload()
}

function ShowSubmit(e) {
    e.preventDefault();labelDiff
    labelDiff("ask",$("input#ask"),$('label#ask-confirm'))
    labelDiff("offer",$("input#offer"),$('label#offer-confirm'))
    $('.codesy_hide').hide()
    $('.codesy_confirm').removeClass('hide')
}

$(document).ready(function() {
  $('form.ajaxSubmit').submit(submitForm)
  $('button#ShowSubmit').click(ShowSubmit)
  $('button#cancelSubmit').click(reloadPlease)
});
