from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.contrib import messages
from . import models as md
import os
# Create your views here.


class QueryBuilderGUI(View):

    def get(self, request, *args, **kwargs):
		context={}
		return render(request,'queryapp/querybuilderGUI.html',context)


class CustomMongoQuery(View):

    def get(self, request, *args, **kwargs):
		context={}
		return render(request,'queryapp/createmongoquery.html',context)



class CustomPythonQuery(View):

    def get(self, request, *args, **kwargs):
		context={}
		return render(request,'queryapp/pythonquery.html',context)


class Createfeature(View):

    def get(self, request, *args, **kwargs):
		context={}
		return render(request,'queryapp/createfeature.html',context)

