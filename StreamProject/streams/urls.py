from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^streams/$', views.my_stream_list, name='my_stream_list'),
    url(r'^my_stream_details/(?P<user_name>.+)/$', views.my_stream_detail, name='my_stream_details'),
    url(r'^$', views.stream_list, name='stream_list'),
    url(r'^stream_details/(?P<user_id>\d+)/$', views.stream_detail, name='stream_details'),
    url(r'^stream_create/$', views.stream_create, name='stream_create'),
    url(r'^search/$', views.stream_search, name='stream_search'),
]