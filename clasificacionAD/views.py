from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
import pandas as pd               
import numpy as np
import matplotlib              
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import seaborn as sns 
import io 
import urllib, base64
from sklearn import model_selection
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import classification_report, RocCurveDisplay
from sklearn.metrics import accuracy_score
from array import array
from sklearn.tree import export_text
import matplotlib.cm as cm
import json
import random

classes="table table-striped table-hover table-wrapper"

def procesamiento(request):
  if not settings.DATOS:
    return redirect('../')
  data={}
  df=settings.DATOS[settings.VERSION]
  data['columTotal']=df.select_dtypes(exclude='object').columns
  data['columnas']=df.select_dtypes(exclude='object').columns
  data['columnasT']=df.columns
  plt.clf()
  figure(figsize=(14,9))
  corr=np.triu(df.corr(numeric_only=True))
  sns.heatmap(df.corr(numeric_only=True),cmap='RdBu_r',annot=True,mask=corr)
  plt.title('Mapa de calor')
  fig=plt.gcf()
  buf=io.BytesIO()
  fig.tight_layout()
  fig.savefig(buf,format='svg')
  plt.figure(figsize=(20,20))
  buf.seek(0)
  string=base64.b64encode(buf.read())
  uri=urllib.parse.quote(string)
  data['MapaCalor']=uri
  data['MatrizCorr']=df.corr(numeric_only=True).to_html(justify='left', classes=classes)
  data['dataFram']=(df.dropna()).to_html(max_rows=12, justify='left', classes=classes)
  return render(request,'../templates/clasificacionAD/clasificacionAD.html',{'data':data})


def graficaComparativa(request):
  if request.method=='POST':
    columnas=request.POST.getlist('col[]','')
    if len(columnas)==0:
      return HttpResponse('')
    df=settings.DATOS[settings.VERSION]
    data=[]
    plt.close()
    plt.clf() 
    figure(figsize=(5,5))
    sns.set()
    plt.scatter(df[columnas[0]], df[columnas[1]], c = df.Outcome)
    plt.xlabel(columnas[0])
    plt.ylabel(columnas[1])
    fig=plt.gcf()
    buf=io.BytesIO()
    fig.savefig(buf,format='svg')
    buf.seek(0)
    string=base64.b64encode(buf.read())
    uri=urllib.parse.quote(string)
    data.append(uri)
    uri=''
    
    data=json.dumps(data)
    return HttpResponse(data)
  
def realizarClasificacionArbol(request):
  if request.method=='POST':
    test=request.POST.get('test')
    depth=request.POST.get('depth')
    minLeaf=request.POST.get('leaf')
    minNode=request.POST.get('node')
    Xvars=request.POST.getlist('x[]')
    Yvar=request.POST['y']
    df=settings.DATOS[settings.VERSION]
    df=df.dropna()
    dfX=df[Xvars]
    X=np.array(dfX)
    data={}
    data['X']=dfX.to_html(max_rows=12, justify='center', classes=classes)
    Y=np.array(df[Yvar])
    data['Y']=pd.DataFrame(df[Yvar]).to_html(max_rows=12, justify='left', classes=classes)
    if not test:
      X_train,X_test,Y_train,Y_test=model_selection.train_test_split(X,Y,test_size=0.2,random_state=0,shuffle=True)
    else:
      X_train,X_test,Y_train,Y_test=model_selection.train_test_split(X,Y,test_size=float(test),random_state=0,shuffle=True)
    
    data['XYtrain']=len(X_train)
    data['XYvalid']=len(X_test)

    data['Xtest']=pd.DataFrame(X_test,columns=Xvars).to_html(max_rows=12, justify='left', classes=classes)
    if not depth and not minNode and not minLeaf:
      clasificacionAD= DecisionTreeClassifier(random_state=0)
    else:
      clasificacionAD= DecisionTreeClassifier(random_state=0, max_depth=int(depth),min_samples_leaf=int(minLeaf),min_samples_split=int(minNode))
    clasificacionAD.fit(X_train,Y_train)
    Y_clasificacion=clasificacionAD.predict(X_test)
    data['clasifFinal']=pd.DataFrame(Y_clasificacion).to_html(justify='left', classes=classes)
    data['crosstab']=pd.crosstab(Y_test,Y_clasificacion,rownames=['Reales'],colnames=['Clasificación']).to_html(justify='left', classes=classes)
    data['Ycomp']=pd.DataFrame({'Real':Y_test,'Estimado':Y_clasificacion}).to_html(max_rows=12, justify='left', classes=classes)
    data['r2']=accuracy_score(Y_test,Y_clasificacion)
    report=classification_report(Y_test,Y_clasificacion,output_dict=True)
    data['report']=pd.DataFrame(report).transpose().to_html(justify='left', classes=classes)
    data['criterio']=clasificacionAD.criterion
    data['matrizImport']=list(clasificacionAD.feature_importances_)
    data['impVar']=pd.DataFrame({'Variable':list(dfX.columns),
    'Importancia':clasificacionAD.feature_importances_}).sort_values('Importancia',ascending=False).to_html(justify='left', classes=classes)
    data['reglas']=export_text(clasificacionAD,feature_names=list(dfX.columns))

    plt.close()
    sns.set()
    plt.clf()
    plt.plot(Y_test,color='red',marker='+',label='Real')
    plt.plot(Y_clasificacion,color='green',marker='+',label='Estimado')
    plt.legend()
    fig=plt.gcf()
    fig.tight_layout()
    buf=io.BytesIO()
    fig.savefig(buf,format='svg')
    buf.seek(0)
    string=base64.b64encode(buf.read())
    uri=urllib.parse.quote(string)
    data['uri']=uri
    plt.clf()
    uri=''
    plt.close()
    sns.set(rc={"figure.figsize":(15,15)})
    plt.clf()
    figure(figsize=(15,15))
    plot_tree(clasificacionAD,feature_names=list(dfX.columns),fontsize=7.5)
    fig=plt.gcf()
    fig.tight_layout()
    buf=io.BytesIO()
    fig.savefig(buf,format='svg')
    buf.seek(0)
    string=base64.b64encode(buf.read())
    uri=urllib.parse.quote(string)
    data['tree']=uri

    plt.close()
    sns.set(rc={"figure.figsize":(6,6)})
    plt.clf()
    figure(figsize=(6,6))
    RocCurveDisplay.from_estimator(clasificacionAD,X_test,Y_test)
    fig=plt.gcf()
    fig.tight_layout()
    buf=io.BytesIO()
    fig.savefig(buf,format='svg')
    buf.seek(0)
    string=base64.b64encode(buf.read())
    uri=urllib.parse.quote(string)
    data['curvaRoc']=uri

    data=json.dumps(data)
    return HttpResponse(data)
  
def limpiarDf(request):
  if request.method=='POST':
    columnas=request.POST.getlist('columns[]')
    df=settings.DATOS[settings.VERSION]
    df=df.drop(columnas,axis=1).dropna()
    settings.DATOS.append(df)
    return HttpResponse('OK') 

def newClas(request):
  if request.method=='POST':
    test=request.POST.get('test')
    depth=request.POST.get('depth')
    minLeaf=request.POST.get('leaf')
    minNode=request.POST.get('node')
    pregnancies=request.POST.get('pregnancies')
    glucose=request.POST.get('glucose')
    bloodPressure=request.POST.get('bloodPressure')
    skinThickness=request.POST.get('skinThickness')
    insulin=request.POST.get('insulin')
    bmi=request.POST.get('bmi')
    diabetesPedigreeFunction=request.POST.get('diabetesPedigreeFunction')
    age=request.POST.get('age')
    Xvars=request.POST.getlist('x[]')
    Yvar=request.POST['y']
    df=settings.DATOS[settings.VERSION]
    df=df.dropna()
    dfX=df[Xvars]
    X=np.array(dfX)
    data={}
    Y=np.array(df[Yvar])

    if not test:
      X_train,X_test,Y_train,Y_test=model_selection.train_test_split(X,Y,test_size=0.2,random_state=0,shuffle=True)
    else:
       X_train,X_test,Y_train,Y_test=model_selection.train_test_split(X,Y,test_size=float(test),random_state=0,shuffle=True)

    if not depth and not minLeaf and not minNode:
      clasificacionAD=DecisionTreeClassifier(random_state=0)
    else:
      clasificacionAD= DecisionTreeClassifier(random_state=0,max_depth=int(depth),min_samples_leaf=int(minLeaf),min_samples_split=int(minNode))
    
    clasificacionAD.fit(X_train,Y_train)
    
    newClas = pd.DataFrame({'Pregnancies': [int(pregnancies)], 'Glucose': [int(glucose)], 'BloodPressure': [int(bloodPressure)], 'SkinThickness': [int(skinThickness)],'Insulin': [int(insulin)],'BMI': [float(bmi)], 'DiabetesPedigreeFunction': [float(diabetesPedigreeFunction)], 'Age': [int(age)]})
    data['newClas']=pd.DataFrame(clasificacionAD.predict(newClas)).to_html(index=False, header=False, justify='center', classes=classes)

    data=json.dumps(data)
    return HttpResponse(data)



