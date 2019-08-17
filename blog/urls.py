from django.conf.urls import url
from . import views

app_name='blog'

urlpatterns = [
    url(r'^$', views.post_list, name='post_list'),
    url(r'^search/$', views.post_search, name='post_search'),
    url(r'^(?P<tag_slug>[-\w]+)/$', views.post_list, name='post_list_tags'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        views.post_detail, name='post_detail'),
    url(r'^share/(?P<id>\d+)/$', views.post_share, name='post_share'),
    
]