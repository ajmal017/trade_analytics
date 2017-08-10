from django.conf.urls import url
from django.conf.urls import include
from . import views

app_name = 'homepage'
urlpatterns = [
    url(r'^homepage$', views.HomePage2, name='home'),

    url(r'^$', views.Welcome, name='welcome'),

    url(r'^boot$', views.Boot, name='boot'),


    url(r'^register/$', views.register, name='register'), # ADD NEW PATTERN!

    url(r'^login/$', views.user_login, name='login'),

    url(r'^logout/$', views.user_logout, name='logout'),

    
    
]