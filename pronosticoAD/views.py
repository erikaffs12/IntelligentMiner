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
from sklearn.tree import DecisionTreeRegressor, plot_tree, export_text
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import json

classes="table table-striped table-hover table-wrapper"


def procesamiento(request):
  if not settings.DATOS:
    return redirect('../')
  data={
  }
  df=settings.DATOS[-1]
  data['columnas']=df.select_dtypes(exclude='object').columns
  return render(request,'../templates/pronosticoAD/pronosticoAD.html',{'data':data})

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
    plt.plot(df[columnas],label=columnas)

    plt.legend()
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
  
def realizarPronosticoArbol(request):
  if request.method=='POST':
    test=request.POST.get('test')
    depth=request.POST.get('depth')
    minLeaf=request.POST.get('leaf')
    minNode=request.POST.get('node')
    Xvars=request.POST.getlist('x[]')
    Yvar=request.POST['y']
    df=settings.DATOS[-1]
    df=df.select_dtypes(exclude='object').dropna()
    dfX=df[Xvars]
    X=np.array(dfX)
    data={}
    data['X']=pd.DataFrame(X).to_html(max_rows=12, justify='left', classes=classes)
    Y=np.array(df[Yvar])
    data['Y']=pd.DataFrame(Y).to_html(max_rows=12, justify='left', classes=classes)

    if not test:
      X_train,X_test,Y_train,Y_test=model_selection.train_test_split(X,Y,test_size=0.2,random_state=0,shuffle=True)
    else:
       X_train,X_test,Y_train,Y_test=model_selection.train_test_split(X,Y,test_size=float(test),random_state=0,shuffle=True)

    data['Xtest']=pd.DataFrame(X_test).to_html(max_rows=12, justify='left', classes=classes)

    if not depth and not minLeaf and not minNode:
      pronosticoAD=DecisionTreeRegressor(random_state=0)
    else:
      pronosticoAD= DecisionTreeRegressor(random_state=0,max_depth=int(depth),min_samples_leaf=int(minLeaf),min_samples_split=int(minNode))
    
    pronosticoAD.fit(X_train,Y_train)
    Y_pronostico=pronosticoAD.predict(X_test)
    data['Ycomp']=pd.DataFrame({'Real':Y_test,'Estimado':Y_pronostico}).to_html(max_rows=12, justify='left', classes=classes)
    data['prono']=pd.DataFrame(Y_pronostico).to_html(max_rows=12, justify='left', classes=classes)
    data['r2']=r2_score(Y_test,Y_pronostico)
    data['matrizImport']=list(pronosticoAD.feature_importances_)
    data['criterio']=pronosticoAD.criterion
    data['impVar']=pd.DataFrame({'Variable':list(dfX.columns),
    'Importancia':pronosticoAD.feature_importances_}).sort_values('Importancia',ascending=False).to_html(justify='left', classes=classes)
    data['mae']=mean_absolute_error(Y_test,Y_pronostico)
    data['mse']=mean_squared_error(Y_test,Y_pronostico)
    data['rmse']=mean_squared_error(Y_test,Y_pronostico,squared=False)
    data['reglas']=export_text(pronosticoAD,feature_names=list(dfX.columns))

    plt.close()
    sns.set()
    plt.clf()
    figure(figsize=(15,5))
    plt.plot(Y_test,color='red',marker='+',label='Real')
    plt.plot(Y_pronostico,color='green',marker='+',label='Estimado')
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
    plot_tree(pronosticoAD,feature_names=list(dfX.columns),fontsize=7.5)
    fig=plt.gcf()
    fig.tight_layout()
    buf=io.BytesIO()

    fig.savefig(buf,format='svg')
    buf.seek(0)
    string=base64.b64encode(buf.read())
    uri=urllib.parse.quote(string)
    data['tree']=uri

    data=json.dumps(data)
    return HttpResponse(data)
  
def newProno(request):
  if request.method=='POST':
    test=request.POST.get('test')
    depth=request.POST.get('depth')
    minLeaf=request.POST.get('leaf')
    minNode=request.POST.get('node')
    valOpen=request.POST.get('valOpen')
    valHigh=request.POST.get('valHigh')
    valLow=request.POST.get('valLow')
    Xvars=request.POST.getlist('x[]')
    Yvar=request.POST['y']
    df=settings.DATOS[-1]
    df=df.select_dtypes(exclude='object').dropna()
    dfX=df[Xvars]
    X=np.array(dfX)
    data={}
    Y=np.array(df[Yvar])

    if not test:
      X_train,X_test,Y_train,Y_test=model_selection.train_test_split(X,Y,test_size=0.2,random_state=0,shuffle=True)
    else:
       X_train,X_test,Y_train,Y_test=model_selection.train_test_split(X,Y,test_size=float(test),random_state=0,shuffle=True)

    if not depth and not minLeaf and not minNode:
      pronosticoAD=DecisionTreeRegressor(random_state=0)
    else:
      pronosticoAD= DecisionTreeRegressor(random_state=0,max_depth=int(depth),min_samples_leaf=int(minLeaf),min_samples_split=int(minNode))
    
    pronosticoAD.fit(X_train,Y_train)
    
    newPron = pd.DataFrame({'Open': [float(valOpen)], 'High': [float(valHigh)], 'Low': [float(valLow)]})
    data['newPron']=pd.DataFrame(pronosticoAD.predict(newPron)).to_html(index=False, header=False, justify='left', classes=classes)

    data=json.dumps(data)
    return HttpResponse(data)

