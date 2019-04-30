from django.conf.urls import url
from tweets.api.views import (
    TweetListAPIView,
    )
from django.views.generic.base import RedirectView
from .views import AccountListAPIView


urlpatterns = [
    url(r'^(?P<username>[\w.@+-]+)/tweet/$', TweetListAPIView.as_view(), name='list'),
    url(r'^account/$', AccountListAPIView.as_view(), name='list'),
]
