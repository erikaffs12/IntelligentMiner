from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
import pandas as pd
# Create your views here.

classes="table table-striped table-hover table-wrapper"

def historial(request):
  if not settings.DATOS:
    return redirect('../')
  if request.method=='POST':
    version=request.POST.get('ver')
    version=int(version)-1
    if version>len(settings.DATOS)-1:
      settings.VERSION=-1
    else:
      settings.VERSION=version
  data={}
  data['df']=settings.DATOS[settings.VERSION].to_html(max_rows=12, justify='left', classes=classes)
  if settings.VERSION==-1:
    data['actver']=len(settings.DATOS)
  else:
    data['actver']=settings.VERSION+1
  data['vers']=len(settings.DATOS)
  return render(request,'../templates/historico/historico.html',context={'data':data})
