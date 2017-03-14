from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import restviews

urlpatterns = [
	# REST api views
    url(r'^stockmeta/$', restviews.StockmetaList.as_view()),
    url(r'^stockmeta/(?P<pk>[0-9]+)/$', restviews.StockmetaDetail.as_view()),


]



urlpatterns = format_suffix_patterns(urlpatterns)