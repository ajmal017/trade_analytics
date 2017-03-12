from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
import os

theme_folder='boostsb_theme'

class Index(View):

    def get(self, request, *args, **kwargs):
		context={}
		return render(request,os.path.join('home',theme_folder,'index.html'),context)