from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.contrib import messages
from . import models as md
import os

theme_folder=''

class Create_Watchlist(View):
    def get(self, request, *args, **kwargs):
		context={}
		return render(request,'stockapp/create_watchlist.html',context)



class View_Watchlist(View):
    def get(self, request, *args, **kwargs):
		md.Stockmeta.objects.all().values()
		headers=['Symbol','Company','Sector','Industry','Status','Labels']
		stockdata=md.Stockmeta.objects.all().values('Symbol','Company','Sector','Industry','Status','Labels')

		context={'headers':headers,'stockdata':stockdata}
		return render(request,'stockapp/view_watchlist.html',context)