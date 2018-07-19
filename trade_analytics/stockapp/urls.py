from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import restviews
from . import views


urlpatterns = [
    # REST api views
    url(r'^stockmeta/$', restviews.StockmetaList.as_view()),
    url(r'^stockmeta/(?P<pk>[0-9]+)/$', restviews.StockmetaDetail.as_view()),

    # views
    url(r'^create_watchlist/$',
        views.Create_Watchlist.as_view(),
        name="create_watchlist"),
    url(r'^view_watchlist/$',
        views.View_Watchlist.as_view(),
        name="view_watchlist"),

]


urlpatterns = format_suffix_patterns(urlpatterns)
