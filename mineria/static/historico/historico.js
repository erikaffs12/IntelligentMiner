function version() {
  $.ajax({
    type: 'POST',
    url: '',
    data: {
      ver: $('#version').val(),
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    },
    success: function () {
      window.location.reload()
    }
  })
}