from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from matplotlib.pyplot import figure
import pandas as pd               
import numpy as np
import matplotlib              
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns 
import io
import urllib, base64
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import json
# Create your views here.

classes="table table-striped table-hover table-wrapper"

def acpd(request):
  if not settings.DATOS:
    return redirect('../') 
  data={}
  df=settings.DATOS[-1]
  data['columTotal']=df.select_dtypes(exclude='object').columns
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
  return render(request,'../templates/acpd/acpd.html',context={'data':data})

def datosPredeterminados(request):
  if request.method=='POST':
    std=request.POST['std']
  data={}
  df= settings.DATOS[-1]
  if std=='MinMaxScaler':
    Estandarizar= MinMaxScaler()
  elif std=='StandardScaler':
    Estandarizar= StandardScaler()
  df1=df.dropna()
  MEstandarizada= Estandarizar.fit_transform(df1.select_dtypes(exclude='object'))
  aux= pd.DataFrame(df.select_dtypes(exclude='object'))
  dfEstandar= pd.DataFrame(MEstandarizada,columns=aux.columns).to_html(table_id='Matrix', justify='left', classes=classes)
  data['mestandarizada']=dfEstandar
  pca=PCA(n_components=10) 
  pca.fit(MEstandarizada)
  varianzas= pca.explained_variance_ratio_
  conteo=0
  numeroComponente=0
  for i in range(0,len(varianzas)):
    if conteo>=0.75:
      if conteo+varianzas[i]<=0.9:
        conteo+=varianzas[i]
      else:
        numeroComponente=i
        break
    else:
      conteo+=varianzas[i]
  data['compon']=pd.DataFrame((pca.components_),columns=aux.columns).to_html(table_id='Matrix2', justify='left', classes=classes)
  data['cargas']=pd.DataFrame(abs(pca.components_),columns=aux.columns).to_html(table_id='Matrix3', justify='left', classes=classes)
  data['var']=conteo
  data['com']=numeroComponente
  plt.close()
  sns.set()
  plt.clf()
  figure(figsize=(5,5))
  sns.lineplot(np.cumsum(pca.explained_variance_ratio_))
  fig=plt.gcf()
  plt.xlabel('Número de componentes')
  plt.ylabel('Varianza acumulada')
  fig.tight_layout()
  buf=io.BytesIO()
  fig.savefig(buf,format='svg')
  buf.seek(0)
  string=base64.b64encode(buf.read())
  uri=urllib.parse.quote(string)
  data['curva']=uri
  uri=None
  data['columnas']=list(df.select_dtypes(exclude='object').columns)
  data=json.dumps(data)
  return HttpResponse(data)
  
def graficaComparativa(request):
  if request.method=='POST':
    df=settings.DATOS[-1]
    data={}
    hue=request.POST['variable']
    plt.close()
    sns.set()
    plt.clf()
    figure(figsize=(4,4))
    if df.shape[0]<1000:
      sns.pairplot(df,hue=hue,dropna=True)
    else:
      sns.pairplot(df.sample(1000),hue=hue,dropna=True)
    fig=plt.gcf()
    fig.tight_layout()
    buf=io.BytesIO()
    fig.savefig(buf,format='svg')
    buf.seek(0)
    string=base64.b64encode(buf.read())
    uri=urllib.parse.quote(string)
    data['columnas']=list(df.select_dtypes(exclude='object').columns)
    data['hue']=uri
    data=json.dumps(data)
    return HttpResponse(data)
    
def graficaDispersion(request):
  if request.method=='POST':
    df=settings.DATOS[-1]
    hue=request.POST['hue']
    v1=request.POST['var1']
    v2=request.POST['var2']
    plt.close()
    sns.set()
    plt.clf()
    figure(figsize=(4,4))
    sns.scatterplot(x=v1,y=v2,data=df,hue=hue)
    fig=plt.gcf()
    fig.tight_layout()
    buf=io.BytesIO()
    fig.savefig(buf,format='svg')
    buf.seek(0)
    string=base64.b64encode(buf.read())
    uri=urllib.parse.quote(string)
    data=json.dumps(uri)
    return HttpResponse(data)

def unaMatrizCorr(request):
  if request.method=='POST':
    df=settings.DATOS[-1]
    data={}
    seleccionUna=request.POST['variableM']
    data['MatrizCorrelaInd']=list(df.corr(numeric_only=True))
    data=json.dumps(data)
    return HttpResponse(data)
    
def limpiarDf(request):
  if request.method=='POST':
    columnas=request.POST.getlist('columns[]')
    df=settings.DATOS[settings.VERSION]
    df=df.drop(columnas,axis=1).dropna()
    settings.DATOS.append(df)
    return HttpResponse('OK') 

  
