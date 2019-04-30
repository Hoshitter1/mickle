"""new_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from posts import views
from tweets import views as views_tweets
from hashtag.views import HashTagView
from tweets.api import views as views_tweets_api
from hashtag.api.views import TagTweetAPIView
from accounts.views import UserRegisterView
import debug_toolbar
import notifications.urls

urlpatterns = [
    url(r'^about/$',views_tweets.aboutView.as_view(), name='about_2'),
    url(r'^__debug__/', include(debug_toolbar.urls)),
    url(r'^admin_django/', admin.site.urls),
    url(r'^practice/$', views_tweets.PracticeTemplateView.as_view(), name='practice'),
    url(r'^search/$', views_tweets.SearchView.as_view(), name='search'),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^$', views_tweets.TweetListView.as_view(), name='home'),
    url(r'^$', views_tweets.TweetListView.as_view(), name='signin'),
    url(r'^api/search/$', views_tweets_api.SearchTweetAPIView.as_view(), name='search-api'),
    url(r'^api/tags/(?P<hashtag>.*)/$', TagTweetAPIView.as_view(), name='tag-tweet-api'),
    url(r'^tags/(?P<hashtag>.*)/$', HashTagView.as_view(), name='hashtag'),
    url(r'^tweet/', include(('tweets.urls', 'tweet'),)),
    url(r'^api/tweet/', include(('tweets.api.urls', 'tweet-api'),)),
    url(r'^api/', include(('accounts.api.urls', 'profiles-api'),)),
    url(r'^register/$', UserRegisterView.as_view(), name='register'),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^', include(('accounts.urls', 'profiles'),)),

    url(r'^posts/', include('posts.urls')),
    url(r'^posts/(?P<post_id>[0-9]+)/$', views.post_detail, name='post_detail'),
    url(r'^hoshito/', views.hoshito, name='hoshito'),
    url(r'^hoshito/test/$', views.hoshito_test, name='hoshito_test'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
