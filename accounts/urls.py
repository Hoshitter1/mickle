from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from .views import (
    UserDetailView,
    UserFollowView,
    UserPointsView,
    model_form_upload,
    PasswordUpdate,
    EmailUpdate,
    NameUpdate,
    CreateDoneView,
    CreateCompleteView,
    Purchase_tsubuyaki,
    SettingView,
    UserDeleteView,
    PurchasePointsView,
    purchase_successView,
    CancelView,
    PontsView,
    NotificationView,
    MickleView,
    StockedMickleView
    )
from django.views.generic.base import RedirectView
from . import views


urlpatterns = [
    url(r'^mickles/$', MickleView.as_view(), name='mickles'),
    url(r'^mickles/stock/$', StockedMickleView.as_view(), name='stocked_mickles'),
    url(r'^setting/$', SettingView.as_view(), name='setting'),
    url(r'^notification/$', NotificationView.as_view(), name='notification'),
    url(r'^setting/points/proceed/$', PontsView.as_view(), name='Process_Points'),
    url(r'^setting/points/purchase/$', PurchasePointsView, name='Purchase_Points'),
    url(r'^create_done/$', CreateDoneView.as_view(), name='done'),
    url(r'^create_complete/(?P<uidb64>[0-9A-Za-z_\-]+)/$', CreateCompleteView.as_view(), name='create_complete'),
    url(r'^(?P<username>[\w.@+-]+)/$', UserDetailView.as_view(), name='detail'),
    url(r'^(?P<username>[\w.@+-]+)/points$', UserPointsView.as_view(), name='points'),
    url(r'^(?P<username>[\w.@+-]+)/follow/$', UserFollowView.as_view(), name='follow'),
    url(r'^(?P<id>\d+)/purchase/$', Purchase_tsubuyaki.as_view(), name='purchase'),
    url(r'^(?P<username>[\w.@+-]+)/update/$', model_form_upload.as_view(), name='update'),
    url(r'^setting/(?P<username>[\w.@+-]+)/password_update/$', PasswordUpdate.as_view(), name='password'),
    url(r'^setting/(?P<username>[\w.@+-]+)/email_update/$', EmailUpdate.as_view(), name='email'),
    url(r'^setting/(?P<pk>\d+)/delete/$', UserDeleteView.as_view(), name='delete'),
    url(r'^setting/(?P<token>[\w.@+-]+)/points/result/$', purchase_successView.as_view(), name='purchase_success'),
    url(r'^setting/(?P<token>[\w.@+-]+)/points/cancel/$', CancelView.as_view(), name='cancel'),
    url(r'^(?P<username>[\w.@+-]+)/name/update/$', NameUpdate.as_view(), name='name'),

]
