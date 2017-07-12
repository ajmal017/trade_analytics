from django.conf.urls import url
from django.conf.urls import include
from . import views

app_name = 'stockdata'
urlpatterns = [

    url(r'^watchlistmanager/view/$', views.ViewStocksWatchLists, name='viewwatchlist'),

    url(r'^watchlistmanager/create/$', views.WatchListManager_create, name='watchlistmanager_create'),

    url(r'^watchlistmanager/amend/$', views.WatchListManager_amend, name='watchlistmanager_amend'),




    url(r'^controlpanel/$', views.ControlPanel, name='controlpanel'),
    
]