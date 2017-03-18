from django.conf.urls import url

from . import views

urlpatterns=[
	url(r'^querybuildergui/$',views.QueryBuilderGUI.as_view(),name='querybuildergui'),
	url(r'^mongoquery/$',views.CustomMongoQuery.as_view(),name='mongoquery'),
	url(r'^pythonquery/$',views.CustomPythonQuery.as_view(),name='pythonquery'),

]


