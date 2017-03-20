from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.contrib import messages

import os

theme_folder='boostsb_theme'

"""
Message level: DEBUG INFO SUCCESS  WARNING ERROR 
"""


class Dashboard(View):

    def get(self, request, *args, **kwargs):
		context={}
		messages.debug(request, '%s SQL statements were executed.' % 33)
		messages.info(request, 'Three credits remain in your account.')
		messages.success(request, 'Profile details updated.')
		messages.warning(request, 'Your account expires in three days.')
		messages.error(request, 'Document deleted.')
		messages.debug(request, 'variable set')
		return render(request,os.path.join('home',theme_folder,'index.html'),context)


class Home(View):

    def get(self, request, *args, **kwargs):
		context={}
		return render(request,os.path.join('home',theme_folder,'home.html'),context)