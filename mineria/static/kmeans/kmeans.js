function limpiarImagenes(id) {
    const imagenes = document.querySelector(id);
    let imagen = imagenes.lastElementChild;
    while (imagen) {
      imagenes.removeChild(imagen);
      imagen = imagenes.lastElementChild
    }
}
     
function limpiarSecciones() {
  idList = ['#X', '#Y', '#Ycomp', '#score', '#predInfo', '#reglas', '#report', '#curvaRoc', '#dfImport', '#XYtrain', '#XYvalid', '#clasFinal', '#crossTa', '#tree', '#newC', '#global11', "#nuevC"]
  idList.forEach(element => limpiarImagenes(element));
}
    
$(document).on('submit', '#graficas', function (e) {
    e.preventDefault();
    let columnas = $('#columnas').val()
    if (columnas.length < 2){
        alert('Selecciona DOS variables')
        return
    }
    if (columnas.length > 2){
        alert('Por favor selecciona únicamente DOS variables')
        return
    }
    $.ajax({
        type: 'POST',
        url: '/graficaComparativaK',
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
  
function realizarClasificacionBosque() {
    let valX = $('#xbosque').val()
    if (valX.length == 0){
      alert('Selecciona las variables predictoras (X):')
      return
    }
    $.ajax({
    type: 'POST',
    url: '/clasificacionK',
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
        
        const valX = $('#X');
        valX.append(obj['X']);

        const valY = $('#Y');
        valY.append(obj['Y']);

        const Ycomp = $('#Ycomp');
        Ycomp.append(obj['Ycomp']);

        const scoreInd = $('#score');
        scoreInd.append('<p class="font-monospace"><b>Score:</b> ' + obj['r2'] + '</p>');

        const reglas = $('#reglas');
        reglas.append(obj['reglas'])

        const predInfo = $('#predInfo');
        predInfo.append('<p class="font-monospace"><b>Criterio:</b> ' + obj['criterio'] + '</p>');
        predInfo.append('<p class="font-monospace"><b>Importancia variables:</b> </p>' + ' [' + obj['matrizImport'] + '] </p>');
        predInfo.append('<p class="font-monospace"><b>Exactitud:</b> ' + obj['r2'] + '</p>');

        const report = $('#report');
        report.append(obj['report'])
    
        const dfImport = $('#dfImport');
        dfImport.append(obj['impVar'])

        const XYtrain = $('#XYtrain');
        mens0 = "Aquí internamente se realiza la selección de los datos para X y para Y que serán utilizados como entrenamiento y como prueba de acuerdo con el test_size ingresado anteriormente. <br> A continuación se muestra cuántos de los datos se eligieron como prueba y cuántos como entrenamiento: <br><br>"
        XYtrain.append(mens0);
        XYtrain.append('<p class="font-monospace"><b>Cantidad de los datos seleccionados para entrenamiento:</b> ' + obj['XYtrain'] + '</p>');

        const XYvalid = $('#XYvalid');
        XYvalid.append('<p class="font-monospace"><b>Cantidad de los datos seleccionados para validación:</b> ' + obj['XYvalid'] + '</p>');

        const clasFinal = $('#clasFinal');
        clasFinal.append(obj['clasifFinal'])

        const crossTa = $('#crossTa');
        crossTa.append(obj['crosstab'])
    
        const predGraph = $('#predGraph');
        predGraph.append('<img src="data:image/svg+xml;base64,' + obj['uri'] + '">');
        const tree = $('#tree');
        tree.append('<img class="img-fluid" src="data:image/svg+xml;base64,' + obj['tree'] + '">');

        const roc = $('#curvaRoc');
        roc.append('<img class="img-fluid" src="data:image/svg+xml;base64,' + obj['curvaRoc'] + '">');
        }
    });
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

function realizarNuevaClas() {
  let edad = $('#age').val()
  if (edad %1 != 0){
    alert("La edad tiene que ser un número entero.");
  }
  let embarazos = $('#pregnancies').val()
  if (embarazos %1 != 0){
    alert("El número de embarazos tiene que ser un número entero.");
  }

  $.ajax({
    type: 'POST',
    url: '/clasificacionNuevaArbol',
    data: {
      test: $('#testBosque').val(),
      x: $('#xbosque').val(),
      y: $('#ybosque').val(),
      arboles: $('#numArboles').val(),
      depth: $('#leafsBosque').val(),
      leaf: $('#leafsBosque').val(),
      node: $('#nodesBosque').val(),
      pregnancies: $('#pregnancies').val(),
      glucose: $('#glucose').val(),
      bloodPressure: $('#bloodPressure').val(),
      skinThickness: $('#skinThickness').val(),
      insulin: $('#insulin').val(),
      bmi: $('#bmi').val(),
      diabetesPedigreeFunction: $('#diabetesPedigreeFunction').val(),
      age: $('#age').val(),
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    },
    success: function (data) {
      let obj = JSON.parse(data);

      const newC = $('#newC');
      newC.append(obj['newClas'])
    }
  });
}