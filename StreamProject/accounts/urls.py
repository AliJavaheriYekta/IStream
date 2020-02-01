from django.conf.urls import url
from django.contrib.auth.views import login, logout, logout_then_login, password_change, password_change_done, password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from . import views

urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^edit/$', views.edit, name='edit'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^logout_then_login/$', logout_then_login, name='logout_then_login'),
    url(r'^password-change/$', password_change, name='password_change'),
    url(r'^password-change/done/$', password_change_done, name='password_change_done'),
    url(r'^password-reset/$', password_reset, name='password_reset'),
    url(r'^password-reset/done/$', password_reset_done, name='password_reset_done'),
    url(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$', password_reset_confirm, name='password_reset_confirm'),
    url(r'^password-reset/complete/$', password_reset_complete, name='password_reset_complete'),

    url(r'^users/followers/$', views.user_followers , name='user_followers'),
    url(r'^users/following/$', views.user_following , name='user_following'),
    url(r'^users/books/$', views.user_book_list, name='user_book_list'),
    url(r'^users/streams/$', views.user_streams, name='user_stream_list'),
    url(r'^users/$', views.user_list, name='user_list'),
    url(r'^users/follow/$', views.user_follow, name='user_follow'),
    url(r'^users/(?P<username>.+)/$', views.user_detail, name='user_detail'),


]