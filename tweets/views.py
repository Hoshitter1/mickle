from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
                            DetailView,
                            ListView,
                            CreateView,
                            UpdateView,
                            DeleteView,
                            TemplateView
                            )

from .forms import TweetModelForm
from accounts.forms import ProfileImage, ProfileName
from .models import Tsubuyaki
from .mixins import FormUserNeededMixin, UserOwnerMixin
import logging
from accounts.models import UserProfile,Payment
from django.http import Http404
from coingate_api import CoingateAPI, api_error
from django.conf import settings

logger = logging.getLogger('tweets')
User = get_user_model()



auth_token = settings.AUTH_TOKEN
sand_auth_token = settings.SAND_AUTH_TOKEN



class RetweetView(View):
    def get(self, request, pk, *args, **kwargs):
        tweet = get_object_or_404(Tsubuyaki, pk=pk)
        if request.user.is_authenticated:
            new_tweet = Tsubuyaki.objects.retweet(request.user, tweet)
            return HttpResponseRedirect("/")#(new_tweet.get_absolute_url())
        return HttpResponseRedirect(tweet.get_absolute_url())

class TweetCreateView(FormUserNeededMixin, CreateView):
    form_class = TweetModelForm
    template_name = 'tweets/create_view.html'
    #success_url = "/tweet/create/"

class TweetUpdateView(LoginRequiredMixin, UserOwnerMixin ,UpdateView):
    queryset = Tsubuyaki.objects.all()
    form_class = TweetModelForm
    template_name = 'tweets/update_view.html'
    #success_url = "/tweet/"

class TweetDeleteView(LoginRequiredMixin,UserOwnerMixin,DeleteView):
    model = Tsubuyaki
    template_name = "tweets/delete_confirm.html"
    success_url = reverse_lazy("tweet:list")

    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)


"""
def tweet_create_view(request):
    form = TweetModelForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
    context = {
        "form":form
    }
    return render(request, 'tweets/create_view.html', context)
"""


class TweetDetailView(DetailView):
    template_name = "tweets/detail_view.html"
    queryset = Tsubuyaki.objects.all()


    def get_object(self):
        pk = self.kwargs.get("pk")
        obj = get_object_or_404(Tsubuyaki,pk=pk)
        return obj #Tsubuyaki.objects.get(id=pk)

    def get_context_data(self, *args, **kwargs): #add data not out of database or another mdoel
        context = super(TweetDetailView, self).get_context_data(*args, **kwargs) #inherit data from class
        qs_user_1 = User.objects.filter(username=self.request.user)
        qs_user_2 = UserProfile.objects.filter(user=self.request.user)
        qs = UserProfile.objects.filter(user=self.get_object().user)
        context['image'] = qs.values('image').first()["image"]
        context['name'] = qs.values('name').first()["name"]
        context['real_name'] = qs.values('user').first()["user"]
        context['user_id_1'] =qs_user_1.values('id').first()["id"]
        context['user_id_2'] =qs_user_2.values('id').first()["id"]
        return context


class TweetListView(LoginRequiredMixin, ListView): #get all data
    template_name = "tweets/tweet_list.html"

    def get_queryset(self, *args, **kwargs): #sort data out of database
        qs = Tsubuyaki.objects.all()
        query = self.request.GET.get("q", None)
        if query is not None:
            qs = qs.filter(
                    Q(content__icontains=query) | #two underscore!! __ <-
                    Q(user__username__icontains=query)
                    )
        return qs

    def get_context_data(self, *args, **kwargs): #add data not out of database or another mdoel
        context = super(TweetListView, self).get_context_data(*args, **kwargs) #inherit data from class
        qs_user = User.objects.filter(username=self.request.user)
        from maintenance_mode.utils import get_client_ip_address
        client_ip_1 = get_client_ip_address(self.request)
        logger.info(client_ip_1)
        from ipware import get_client_ip
        client_ip, is_routable = get_client_ip(self.request)
        logger.info(client_ip)
        logger.info(is_routable)

        context['create_form'] = TweetModelForm()
        context['create_form_2'] = ProfileImage()
        context['create_form_3'] = ProfileName()
        context['create_url'] = reverse_lazy("tweet:create")
        context['create_url_2'] = str(self.request.user)+ "/update/"
        qs = UserProfile.objects.filter(user__exact=self.request.user)
        context['points'] = qs.values('points').first()["points"]
        context['name'] = qs.values('name').first()["name"]
        context['image'] = qs.values('image').first()["image"]
        context['user_id_1'] =qs_user.values('id').first()["id"]
        context['user_id_2'] =qs.values('id').first()["id"]
        if context['image'] == "no_img":
            context['image'] = "static/Hiyoko.png"
        logger.info("what's happening???")
        try:
            qs = Payment.objects.filter(user=self.request.user)
            id = qs.values('purchase_id').first()["purchase_id"]
            logger.info(qs)
            logger.info(id)
            try:
                api = CoingateAPI(auth_token=auth_token, environment='live')
                result = api.checkout(id)# if there were no such an order, it would return error
                logger.info(result)
                if result['status'] == 'paid':
                    user_obj = UserProfile.objects.filter(user=self.request.user).first()
                    points_add = qs.values('points').first()["points"]
                    points_original = user_obj.points
                    points = points_original + points_add
                    user_obj.points = points
                    user_obj.save()
                    qs.delete()
                else:
                    logger.info(result['status'])
            except api_error.APIError as e:
                logger.info(e)
        except TypeError as e:
            logger.info(e)
            logger.info(qs)
            logger.info("No data in queryset")
        return context



class SearchView(View):
    def get(self, request, *args, **kwargs):
        query  = request.GET.get("q")
        qs = None
        if query:
            qs = User.objects.filter(
                    Q(username__icontains=query)
                    )
        try:
            qs_1 = User.objects.filter(username=self.request.user)
            qs_2 = UserProfile.objects.filter(user=self.request.user)
            context = {"users": qs,
                        "user_id_1": qs_1.values('id').first()["id"],
                        "user_id_2": qs_2.values('id').first()["id"],
                        }
            logger.info(context)
        except:
            context = {"users": qs,
                        "user_id_1": "99999999",
                        "user_id_2": "99999999",
                        }
        return render(request, "tweets/search.html", context)

    # def get_context_data(self, *args, **kwargs): #add data not out of database or another mdoel
    #     context = super(SearchView, self).get_context_data(*args, **kwargs) #inherit data from class
    #     logger.info(context)
    #     qs = UserProfile.objects.filter(user=self.get_object().user)
    #     qs_user = User.objects.filter(username=self.request.user)
    #     context['image'] = qs.values('image').first()["image"]
    #     context['name'] = qs.values('name').first()["name"]
    #     context['user_id_1'] =qs_user.values('id').first()["id"]
    #     context['user_id_2'] =qs.values('id').first()["id"]
    #     logger.info(context)
    #     return context


def HomeView(request):
    return render(request, "tweets/home.html")

class aboutView(TemplateView):
    template_name = "about_2.html"




# class PracticeTemplateView(TemplateView):
#     template_name = "tweets/practice.html"
#
#     def get_context_data(self, *args, **kwargs):
#         context = super(PracticeTemplateView, self).get_context_data(*args, **kwargs)
#         context["foo"] = "bar"
#         return context

class PracticeTemplateView(ListView):
    template_name = "tweets/practice.html"
    model = Tsubuyaki
