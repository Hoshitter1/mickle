from django.conf.urls import url
from .views import (
    SearchTweetAPIView,
    TweetListAPIView,
    TweetCreateAPIView,
    TweetDetailAPIView,
    RetweetAPIView,
    LikeToggleAPIView,
    PointsAPIView,
    MickleAPIView,
    StockedMickleAPIView
)
from django.views.generic.base import RedirectView


urlpatterns = [
    url(r'^purchase/(?P<id>\d+)/$', MickleAPIView.as_view(), name='purchased'),
    url(r'^stocked/(?P<id>\d+)/$', StockedMickleAPIView.as_view(), name='stocked'),
    url(r'^$', TweetListAPIView.as_view(), name='list'),
    # url(r'^search/$', TweetListView.as_view(), name='list'),
    url(r'^create/$', TweetCreateAPIView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/$', TweetDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/like/$', LikeToggleAPIView.as_view(), name='like_toggle'),
    url(r'^(?P<pk>\d+)/retweet/$', RetweetAPIView.as_view(), name='retweet'),
    url(r'^(?P<tsubuyaki_id>\d+)/points/(?P<pk>\d+)/$', PointsAPIView.as_view(), name='points'),
    # url(r'^(?P<pk>\d+)/update/$', TweetUpdateView.as_view(), name='update'),
    # url(r'^(?P<pk>\d+)/delete/$', TweetDeleteView.as_view(), name='delete'),

]
