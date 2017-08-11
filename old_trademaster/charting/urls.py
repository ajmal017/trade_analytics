from django.conf.urls import url
from django.conf.urls import include
from . import views

app_name = 'charting'
urlpatterns = [

    url(r'^quickchart/$', views.Quickchart, name='quickchart'),
    url(r'^savedchart/$', views.GetSavedchart, name='savedchart'),

    url(r'^viewcharts/$', views.ViewCharts, name='viewcharts'),
    # url(r'^tvdatafeed/config/$', views.Tvdatafeedconfig, name='tvdatafeedconfig'),
    url(r'^tvdatafeed/(?P<method>[a-zA-Z0-9_]+)\\?/$', views.Tvdatafeed, name='tvdatafeed'),
    # url(r'^tvdatafeed/config/$', views.Tvdatafeedconfig, name='tvdatafeedconfig'),


]