function limpiarImagenes(id) {
  const imagenes = document.querySelector(id);
  let imagen = imagenes.lastElementChild;
  while (imagen) {
    imagenes.removeChild(imagen);
    imagen = imagenes.lastElementChild
  }
}

function definirEstandarizado() {
  $.ajax({
    type: 'POST',
    url: '/estandarizado',
    data: {
      std: $('#std').val(),
      columns: $('#colHist').val(),
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    },
    success: function (data) {
      const obj = JSON.parse(data)
      const matrix = document.getElementById("Matrix");
      const matrix2 = document.getElementById("Matrix2");
      const matrix3 = document.getElementById("Matrix3");
      let curva = document.getElementById("curva");
      if (matrix) {
        matrix.remove();
      }
      if (matrix2) {
        matrix2.remove();
      }
      if (matrix3) {
        matrix3.remove();
      }
      if (curva) {
        curva.remove();
        const p = document.getElementById('parrafo').remove();
      }
      curva = '<img id="curva" src="data:image/svg+xml;base64,' + obj['curva'] + '">'
      $('#StdMatrix').append(obj['mestandarizada'])
      $('#CovMatrix').append(obj['compon'])
      $('#matrizCargas').append(obj['cargas'])
      $('#elbow').append(curva)
      $('#elbow').append("<p id='parrafo'>Con " + obj['com'] + " componentes se logra " + obj['var'] + " de varianza acumulada, lo cual está dentro del rango.</p>");
      const hue = document.getElementById('hue')
      if (hue)
        return
      let ctag = "<select class='form-select form-select-sm selectAltura4' name='hue' id='hue'>"
      const columnas = obj['columnas']
      const boton = "<button class='btn btn-success boton4' onclick='dibujarHue()'>Dibujar</button>"
      let opciones = ''
      columnas.forEach(element => {
        opciones += "<option>" + element + "</option>"
      });
      ctag += opciones + "</select>"
      const mensaje1 = "<br>"
      const texto1 = "Selecciona la variable para observar la relación entre pares de variables con respecto a esa:"
      $('#hueSection').append(mensaje1)
      $('#hueSection').append(texto1)
      $('#hueSection').append(mensaje1)
      $('#hueSection').append(mensaje1)
      $('#hueSection').append(ctag)
      $('#hueSection').append(mensaje1)
      $('#hueSection').append(boton)
      $('#hueSection').append(mensaje1)
      $('#hueSection').append(mensaje1)
    }
  })
}

function dibujarHue() {
  $.ajax({
    type: 'POST',
    url: '/comparativa',
    data: {
      variable: $('#hue').val(),
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    },
    success: function (data) {
      const obj = JSON.parse(data)
      const hueImg = document.getElementById('hueImg')
      const sep = "<br>"
      if (hueImg)
        hueImg.remove()
      $('#hueSection').append('<img class="img-fluid" id="hueImg" src="data:image/svg+xml;base64,' + obj['hue'] + '" + >')
      $('#hueSection').append(sep)
      $('#hueSection').append(sep)
      const disp = document.getElementById('dispImg')
      if (disp)
        disp.remove()
      let ctag1 = "<select class='form-select form-select-sm selectAltura3' name='hue' id='col1'>"
      let ctag2 = "<select class='form-select form-select-sm selectAltura4' name='hue' id='col2'>"
      const columnas = obj['columnas']
      const boton1 = "<button class='btn btn-success boton2' onclick='dibujarDispersion()'> Comparar </button>"
      const boton2 = "<button class='btn btn-danger boton3' onclick='limpiarImagenes(" + '"#dispersion"' + ")'>Limpiar</button>"
      const mensaje = "También es posible observar cada una de manera individual: "
      let opciones = ''
      columnas.forEach(element => {
        opciones += "<option>" + element + "</option>"
      });
      ctag1 += opciones + "</select>"
      ctag2 += opciones + "</select>"
      $('#hueSection').append(mensaje)
      $('#hueSection').append(sep)
      $('#hueSection').append(sep)
      $('#hueSection').append(ctag1)
      $('#hueSection').append(ctag2)
      $('#hueSection').append(sep)
      $('#hueSection').append(boton1)
      $('#hueSection').append(boton2)
      $('#hueSection').append(sep)
      $('#hueSection').append(sep)
    }
  })
}

function dibujarDispersion() {
  $.ajax({
    type: 'POST',
    url: '/dispersion',
    data: {
      hue: $('#hue').val(),
      var1: $('#col1').val(),
      var2: $('#col2').val(),
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    },
    success: function (data) {
      const obj = JSON.parse(data)
      $('#dispersion').append('<img id="dispIMG" src="data:image/svg+xml;base64,' + obj + '" + >')
    }
  })
}

function limpiarDataFrame() {
  $.ajax({
    type: 'POST',
    url: '/limpiarDf',
    data: {
      columns: $('#quitar').val(),
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    },
    success: function (data) {
      window.location.reload()
    }
  })
}