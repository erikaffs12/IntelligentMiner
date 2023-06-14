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
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, RocCurveDisplay
from sklearn.preprocessing import StandardScaler, MinMaxScaler  
from sklearn.metrics import accuracy_score
from array import array
import matplotlib.cm as cm
from sklearn.cluster import KMeans
from kneed import KneeLocator
from sklearn.metrics import pairwise_distances_argmin_min
from mpl_toolkits.mplot3d import Axes3D

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
  Estandarizar= StandardScaler()
  MEstandarizada= Estandarizar.fit_transform(df.select_dtypes(exclude='object'))
  aux= pd.DataFrame(df.select_dtypes(exclude='object'))
  dfEstandar= pd.DataFrame(MEstandarizada,columns=aux.columns).to_html(table_id='Matrix', justify='left', classes=classes)
  data['mestandarizada']=dfEstandar
  
  SSE = []
  for i in range(2, 10):
    km = KMeans(n_clusters=i, random_state=0)
    km.fit(MEstandarizada)
    SSE.append(km.inertia_)
  
  plt.close()
  sns.set(rc={"figure.figsize":(5,5)})
  plt.clf()
  plt.figure(figsize=(5, 5))
  sns.set()
  #plt.plot(range(2, 10), SSE, marker='o')
  #plt.xlabel('Cantidad de clusters *k*')
  #plt.ylabel('SSE')
  #plt.title('Elbow Method')
  kl = KneeLocator(range(2, 10), SSE, curve="convex", direction="decreasing")
  plt.style.use('ggplot')
  kl.plot_knee()
  fig=plt.gcf()
  buf=io.BytesIO()
  fig.tight_layout()
  fig.savefig(buf,format='svg')
  buf.seek(0)
  string=base64.b64encode(buf.read())
  uri=urllib.parse.quote(string)
  data['graficaCodo']=uri
  data['numeroClus']=kl.elbow

  #Se crean las etiquetas de los elementos en los clusters
  MParticional = KMeans(n_clusters=kl.elbow, random_state=0).fit(MEstandarizada)
  MParticional.predict(MEstandarizada)
  data['etiquetas']=MParticional.labels_
  auxiliar=pd.DataFrame(MParticional.labels_)
  auxiliar.rename(columns = {0:'ClusterP'}, inplace = True)
  DataFinal=pd.concat([auxiliar, df], axis=1).to_html(max_rows=12, justify='left', classes=classes)
  data['clusterPa']=DataFinal

  df['clusterP'] = MParticional.labels_

  data['count']=pd.DataFrame(df.groupby(['clusterP'])['clusterP'].count()).to_html(justify='left', classes=classes)

  data['centroides']=pd.DataFrame(df.groupby('clusterP').mean()).to_html(justify='left', classes=classes)

  plt.clf()
  figure(figsize=(14,9))
  plt.rcParams['figure.figsize'] = (10, 7)
  plt.style.use('ggplot')
  colores=['red', 'blue', 'green', 'yellow']
  asignar=[]
  for row in MParticional.labels_:
      asignar.append(colores[row])
  fig = plt.figure()
  ax = Axes3D(fig)
  ax.scatter(MEstandarizada[:, 0], MEstandarizada[:, 1], MEstandarizada[:, 2], marker='o', c=asignar, s=60)
  ax.scatter(MParticional.cluster_centers_[:, 0], MParticional.cluster_centers_[:, 1], MParticional.cluster_centers_[:, 2], marker='o', c=colores, s=1000)
  fig=plt.gcf()
  buf=io.BytesIO()
  fig.tight_layout()
  fig.savefig(buf,format='svg')
  plt.figure(figsize=(20,20))
  buf.seek(0)
  string=base64.b64encode(buf.read())
  uri=urllib.parse.quote(string)
  data['graficaCluster']=uri

  return render(request,'../templates/kmeans/kmeans.html',{'data':data})


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

def clasificacionK(request):
  if request.method=='POST':
    test=request.POST.get('test')
    arboles=request.POST.get('arboles')
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

    data['X']=dfX.to_html(max_rows=12, justify='left', classes=classes)
    Y=np.array(df[Yvar])
    data['Y']=pd.DataFrame(df[Yvar]).to_html(max_rows=12, justify='left', classes=classes)
    if not test:
      X_train,X_test,Y_train,Y_test=model_selection.train_test_split(X,Y,test_size=0.2,random_state=0,shuffle=True)
    else:
      X_train,X_test,Y_train,Y_test=model_selection.train_test_split(X,Y,test_size=float(test),random_state=0,shuffle=True)

    data['XYtrain']=len(X_train)
    data['XYvalid']=len(X_test)

    data['Xtest']=pd.DataFrame(X_test,columns=Xvars).to_html(max_rows=12, justify='left', classes=classes)
    if not arboles and not depth and not minLeaf and not minNode:
      clasificacionAD= RandomForestClassifier(random_state=0)
    else:
      clasificacionAD= RandomForestClassifier(n_estimators=int(arboles),max_depth=int(depth),min_samples_split=int(minNode),min_samples_leaf=int(minLeaf))
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
    if not arboles:
      estimador=clasificacionAD.estimators_[100]
    else:
      numAr=random.randint(1,int(arboles))
      estimador=clasificacionAD.estimators_[numAr]

    data['reglas']=export_text(estimador,feature_names=list(dfX.columns))
    figure(figsize=(15,15))
    plot_tree(estimador,feature_names=list(dfX.columns),fontsize=7.5)
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
    metrics.RocCurveDisplay.from_estimator(clasificacionAD,X_test,Y_test)
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
    arboles=request.POST.get('arboles')
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

    if not arboles and not depth and not minLeaf and not minNode:
      clasificacionAD=RandomForestClassifier(random_state=0)
    else:
      clasificacionAD= RandomForestClassifier(n_estimators=int(arboles),max_depth=int(depth),min_samples_split=int(minNode),min_samples_leaf=int(minLeaf))
    
    clasificacionAD.fit(X_train,Y_train)
    
    newClas = pd.DataFrame({'Pregnancies': [int(pregnancies)], 'Glucose': [int(glucose)], 'BloodPressure': [int(bloodPressure)], 'SkinThickness': [int(skinThickness)],'Insulin': [int(insulin)],'BMI': [float(bmi)], 'DiabetesPedigreeFunction': [float(diabetesPedigreeFunction)], 'Age': [int(age)]})
    data['newClas']=pd.DataFrame(clasificacionAD.predict(newClas)).to_html(index=False, header=False, justify='center', classes=classes)

    data=json.dumps(data)
    return HttpResponse(data)
