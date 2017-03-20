from django.conf.urls import url

from . import views

urlpatterns=[
url(r'^$',views.Home.as_view(),name='index'),
url(r'^home/$',views.Home.as_view(),name='home'),
url(r'^dashboard/$',views.Dashboard.as_view(),name='dashboard'),

]