from django.conf.urls import url

from . import views

#r = regular expression正規表現　
# r'^$" means If you don't specify file name, call views.index
urlpatterns = [url(r'^$',views.index, name = 'index')]
