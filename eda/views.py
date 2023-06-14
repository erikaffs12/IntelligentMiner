from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from matplotlib.pyplot import figure
from statistics import mode
from collections import Counter
import pandas as pd               
import numpy as np
import matplotlib              
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns 
import io
import urllib, base64
import json
# Create your views here.

classes="table table-striped table-hover table-wrapper"

def edaAsView(request):
  if not settings.DATOS:
    return redirect('../')
  data={
  }
  df=settings.DATOS[-1]
  
  data['types']=typesData(df).to_html(justify='left', classes=classes) #######
  data['info']=infoToDF(df).to_html(justify='left', classes=classes) #######
  data['shape']=df.shape  
  data['columnasNum']=df.select_dtypes(exclude='object').columns
  data['columnasEx']=df.select_dtypes(include='object').columns
  data['describe']=describeToDF(df).to_html()
  plt.clf()
  figure(figsize=(15,10))
  corr=np.triu(df.corr(numeric_only=True))
  sns.heatmap(df.corr(numeric_only=True),cmap='RdBu_r',annot=True,mask=corr)
  plt.title('Mapa de calor')
  fig=plt.gcf()
  buf=io.BytesIO()
  fig.savefig(buf,format='svg')
  fig.tight_layout()
  plt.figure(figsize=(20,20))
  buf.seek(0)
  string=base64.b64encode(buf.read())
  uri=urllib.parse.quote(string)
  data['corr']=uri
  data['matcorr']=df.corr(numeric_only=True).to_html(justify='left', classes=classes)
  data['describe']=describeToDF(df).to_html(justify='left', classes=classes) #####################
  data['describeCat']=describeCat(df).to_html(justify='left', classes=classes) #####################

  return render(request,'../templates/eda/eda.html',context={'data':data})


def graficasHistograma(request):
  if request.method=='POST':
    df=settings.DATOS[-1]
    print(request.POST)
    columnas=request.POST.getlist('columns[]')
    data=[]
    plt.close()
    for columna in columnas:
      plt.clf()
      sns.set(rc={'figure.figsize':(4,4)})
      df.hist(xrot=90,column=columna)
      fig=plt.gcf()
      fig.tight_layout()
      buf=io.BytesIO()
      fig.savefig(buf,format='svg')
      buf.seek(0)
      string=base64.b64encode(buf.read())
      uri=urllib.parse.quote(string)
      data.append(uri)
      plt.close()
    data=json.dumps(data)
    return HttpResponse(data)

def graficasCountplot(request):
  if request.method=='POST':
    data=[]
    df=settings.DATOS[-1]
    columnas=request.POST.getlist('columns[]')
    num=int(request.POST.get('num'))
    plt.close()
    sns.set(rc={'figure.figsize':(4,4)}) 
    for col in columnas:
      if df[col].nunique()<=num:
        plt.clf()
        figure(figsize=(5,5))
        sns.countplot(y=col,data=df)
        plt.title(col)
        fig=plt.gcf()
        fig.tight_layout()
        buf=io.BytesIO()
        fig.savefig(buf,format='svg')
        buf.seek(0)
        string=base64.b64encode(buf.read())
        uri=urllib.parse.quote(string)
        data.append(uri)
    data=json.dumps(data)
    return HttpResponse(data)
    plt.close()

def graficasGato(request):
  if request.method=='POST':
    data=[]
    df=settings.DATOS[-1]
    columnas=request.POST.getlist('columns[]')
    plt.close()
    for col in columnas:
      plt.clf()
      sns.set(rc={'figure.figsize':(4,4)})
      figure(figsize=(4,4))
      sns.boxplot(data=df,x=col)
      plt.title(col)
      fig=plt.gcf()
      fig.tight_layout()
      buf=io.BytesIO()
      fig.savefig(buf,format='svg')
      buf.seek(0)
      string=base64.b64encode(buf.read())
      uri=urllib.parse.quote(string)
      data.append(uri)
      plt.close()
    data=json.dumps(data)
    return HttpResponse(data)

def typesData(data):
  newTypesDF=data.columns.to_frame(name='Column')
  newTypesDF['Dtype']=data.dtypes
  newTypesDF.reset_index(drop=True,inplace=True)
  return newTypesDF

def infoToDF(data):
  newInfoDF=data.columns.to_frame(name='Column')
  newInfoDF['Non-Null Count']=data.notna().sum()
  newInfoDF['Dtype']=data.dtypes
  newInfoDF.reset_index(drop=True,inplace=True)
  return newInfoDF

def describeToDF(data):
  describeDf=[]
  datos=[]
  cols=[]
  for col in data.select_dtypes(exclude="object"):
    datos.append(data[col].count().sum())
  describeDf.extend([datos])
  datos=[]
  for col in data.select_dtypes(exclude="object"):
    datos.append(data[col].mean().sum())
  describeDf.extend([datos])
  datos=[]
  for col in data.select_dtypes(exclude="object"):
    datos.append(data[col].std().sum())
  describeDf.extend([datos])
  datos=[]
  for col in data.select_dtypes(exclude="object"):
    datos.append(data[col].min().sum())
  describeDf.extend([datos])
  datos=[]
  for col in data.select_dtypes(exclude="object"):
    datos.append(data[col].quantile(q=0.25).sum())
  describeDf.extend([datos])
  datos=[]
  for col in data.select_dtypes(exclude="object"):
    datos.append(data[col].quantile().sum())
  describeDf.extend([datos])
  datos=[]
  for col in data.select_dtypes(exclude="object"):
    datos.append(data[col].quantile(q=0.75).sum())
  describeDf.extend([datos])
  datos=[]
  for col in data.select_dtypes(exclude="object"):
    datos.append(data[col].max().sum())
    cols.append(col)
  describeDf.extend([datos])
  newDescribeDf=pd.DataFrame(describeDf,index=['count','mean','std','min','25%','50%','75%','max'],columns=cols)
  return newDescribeDf

def describeCat(data):
  describeCat=[]
  datos=[]
  cols=[]
  var=[]
  for col in data.select_dtypes(include="object"):
    datos.append(data[col].count())
  describeCat.extend([datos])
  datos=[]
  for col in data.select_dtypes(include="object"):
    datos.append(len(data[col].unique()))
  describeCat.extend([datos])
  datos=[]
  data2=data.dropna()
  for col in data2.select_dtypes(include="object"):
    datos.append(mode(data2[col]))
  describeCat.extend([datos])
  datos=[]
  for col in data.select_dtypes(include="object"):
    valorAct=data[col]
    moda, freq=Counter(valorAct).most_common(1)[0]
    datos.append(freq)
    cols.append(col)
  describeCat.extend([datos]) 
  newDescribeCatDf=pd.DataFrame(describeCat,index=['count', 'unique', 'top', 'freq'], columns=cols)
  return newDescribeCatDf


