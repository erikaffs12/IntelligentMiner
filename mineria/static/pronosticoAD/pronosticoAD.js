function limpiarImagenes(id) {
  const imagenes = document.querySelector(id);
  let imagen = imagenes.lastElementChild;
  while (imagen) {
    imagenes.removeChild(imagen);
    imagen = imagenes.lastElementChild
  }
}

function limpiarSecciones() {
  idList = ['#X', '#Y', '#Xtest', '#Ycomp', '#prono', '#predInfo', '#dfImport', '#reglas', '#predGraph', '#tree', '#newP', '#global11', "#nuevP"]
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

function realizarPronosticoArbol() {
  let valX = $('#xarbol').val()
  if (valX.length == 0){
  alert('Selecciona las variables predictoras (X):')
  return
  }

  $.ajax({
    type: 'POST',
    url: '/pronosticoArbol',
    data: {
      test: $('#testArbol').val(),
      x: valX,
      y: $('#yarbol').val(),
      depth: $('#depthArbol').val(),
      leaf: $('#leafsArbol').val(),
      node: $('#nodesArbol').val(),
      valOpen: $('#valOpen').val(),
      valHigh: $('#valHigh').val(),
      valLow: $('#valLow').val(),
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    },
    success: function (data) {
      let obj = JSON.parse(data);
      limpiarImagenes('#X');
      limpiarImagenes('#Y');
      limpiarImagenes('#Xtest');
      limpiarImagenes('#Ycomp');
      limpiarImagenes('#prono');
      limpiarImagenes('#predInfo');
      limpiarImagenes('#dfImport');
      limpiarImagenes('#reglas');
      limpiarImagenes('#predGraph');
      limpiarImagenes('#tree');
      limpiarImagenes('#newP');
      document.getElementById('X').innerHTML = obj['X'];
      document.getElementById('Y').innerHTML = obj['Y'];
      document.getElementById('Xtest').innerHTML = obj['Xtest'];
      document.getElementById('Ycomp').innerHTML = obj['Ycomp'];
      document.getElementById('prono').innerHTML = obj['prono'];

      const predInfo = $('#predInfo');
      predInfo.append('<p class="font-monospace"><b>Score:</b> ' + obj['r2'] + '</p>');
      predInfo.append('<p class="font-monospace"><b>Criterio:</b> ' + obj['criterio'] + '</p>');
      //predInfo.append('<p>Importancia</p>');
      //predInfo.append(obj['impVar'])
      predInfo.append('<p class="font-monospace"><b>Importancia variables:</b> ' + '[' + obj['matrizImport'] + ']' + '</p>');
      predInfo.append('<p class="font-monospace"><b>MAE:</b> ' + obj['mae'] + '</p>');
      predInfo.append('<p class="font-monospace"><b>MSE:</b> ' + obj['mse'] + '</p>');
      predInfo.append('<p class="font-monospace"><b>RMSE:</b> ' + obj['rmse'] + '</p>');

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
    url: '/pronosticoArbolNuevo',
    data: {
      test: $('#testArbol').val(),
      x: $('#xarbol').val(),
      y: $('#yarbol').val(),
      depth: $('#depthArbol').val(),
      leaf: $('#leafsArbol').val(),
      node: $('#nodesArbol').val(),
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