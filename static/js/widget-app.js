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

$(document).ready(function() {
  $('form').submit(submitForm)
});
