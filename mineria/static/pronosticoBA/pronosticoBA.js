function limpiarImagenes(id) {
    const imagenes = document.querySelector(id);
    let imagen = imagenes.lastElementChild;
    while (imagen) {
      imagenes.removeChild(imagen);
      imagen = imagenes.lastElementChild
    }
  }

function limpiarSecciones() {
  idList = ['#X', '#Y', '#Xtest', '#Ycomp', '#prono', '#predInfo', '#dfImport', '#reglas', '#predGraph', '#tree', '#newP', '#global11', '#nuevP']
  idList.forEach(element => limpiarImagenes(element));  
}
  
$(document).on('submit', '#graficas', function (e) {
  e.preventDefault();
  let columnas = $('#columnas').val()
  $.ajax({
    type: 'POST',
    url: '/graficaComparativa', 
    data: {
      col: columnas,
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    },
    success: function (data) {
      const obj = JSON.parse(data)
      const imgArray = []
      for (let i in obj)
        imgArray.push(obj[i])
      let imagen = new Image();
      for (let i in imgArray) {
        $('#img-graficas').append('<img class="img-fluid" src="data:image/svg+xml;base64,' + imgArray[i] + '">')
      }
    }
  })
});

function realizarPronosticoBosque() {
  let valX = $('#xbosque').val()
  if (valX.length == 0){
    alert('Selecciona las variables predictoras (X):')
    return
  } 
  $.ajax({
    type: 'POST',
    url: '/pronosticoBosque',
    data: {
      test: $('#testBosque').val(),
      x: valX,
      y: $('#ybosque').val(),
      arboles: $('#numArboles').val(),
      depth: $('#depthBosque').val(),
      leaf: $('#leafsBosque').val(),
      node: $('#nodesBosque').val(),
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    },
    success: function (data) {
      let obj = JSON.parse(data);
      limpiarImagenes('#X');
      limpiarImagenes('#Y');
      limpiarImagenes('#Xtest');
      limpiarImagenes('#Ycomp');
      limpiarImagenes('#predInfo');
      limpiarImagenes('#predGraph');
      limpiarImagenes('#tree');
      document.getElementById('X').innerHTML = obj['X'];
      document.getElementById('Y').innerHTML = obj['Y'];
      document.getElementById('Xtest').innerHTML = obj['Xtest'];
      document.getElementById('Ycomp').innerHTML = obj['Ycomp'];
      document.getElementById('prono').innerHTML = obj['prono'];
      const predInfo = $('#predInfo');
      predInfo.append('<p class="font-monospace">Score: ' + obj['r2'] + '</p>');
      predInfo.append('<p class="font-monospace">Criterio: ' + obj['criterio'] + '</p>');
      predInfo.append('<p class="font-monospace"><b>Importancia variables:</b> ' + '[' + obj['matrizImport'] + ']' + '</p>');
      predInfo.append('<p class="font-monospace">MAE: ' + obj['mae'] + '</p>');
      predInfo.append('<p class="font-monospace">MSE: ' + obj['mse'] + '</p>');
      predInfo.append('<p class="font-monospace">RMSE: ' + obj['rmse'] + '</p>');

      const dfImport = $('#dfImport');
      dfImport.append(obj['impVar'])

      const reglas = $('#reglas');
      reglas.append(obj['reglas'])

      const newP = $('#newP');
      newP.append(obj['newPron'])

      const predGraph = $('#predGraph');
      predGraph.append('<img class="img-fluid" src="data:image/svg+xml;base64,' + obj['uri'] + '">');
      const tree = $('#tree');
      tree.append('<img class="img-fluid" src="data:image/svg+xml;base64,' + obj['tree'] + '">');
    }
  });
}

function realizarNuevoPronostico() {
  $.ajax({
    type: 'POST',
    url: '/pronosticoBosqueNuevo',
    data: {
      test: $('#testBosque').val(),
      x: $('#xbosque').val(),
      y: $('#ybosque').val(),
      arboles: $('#numArboles').val(),
      depth: $('#depthBosque').val(),
      leaf: $('#leafsBosque').val(),
      node: $('#nodesBosque').val(),
      valOpen: $('#valOpen').val(),
      valHigh: $('#valHigh').val(),
      valLow: $('#valLow').val(),
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    },
    success: function (data) {
      let obj = JSON.parse(data);

      const newP = $('#newP');
      newP.append(obj['newPron'])
    }
  });
}
