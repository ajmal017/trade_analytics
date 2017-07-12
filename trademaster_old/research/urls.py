from django.conf.urls import url
from django.conf.urls import include
from . import views

app_name = 'research'
urlpatterns = [
    
    url(r'^querytool/$', views.QueryTool, name='querytool'),
    url(r'^windowquerytool_advanced/$', views.WindowQueryTool_advanced, name='windowquerytool_advanced'),

    url(r'^createmodifyfeature/$', views.CreateModifyFeature, name='createmodifyfeature'),

    url(r'^categories/$', views.CategoryManager, name='category'),
    url(r'^tagsubmit/$', views.tagsubmit, name='tagsubmit'),
    url(r'^study/$', views.Study, name='study'),
    url(r'^status/$', views.ResearchStatus, name='researchstatus'),

    url(r'^logs/$', views.ComputeLog, name='ComputeLog'),

    url(r'^learning/$', views.Learning, name='learning'),
    
    
    
]