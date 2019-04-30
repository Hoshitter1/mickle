from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Q
from tweets.models import Tsubuyaki
from accounts.models import UserProfile
from .serializers import TweetModelSerializer, TweetModelSerializer_2
from .pagination import StandardResultsPagination
from accounts.api.serializers import UserDisplaySerializer
from accounts.models import UserProfile
import chromelogger as console
import logging
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from notifications.signals import notify
from rest_framework.permissions import BasePermission, SAFE_METHODS

logger = logging.getLogger('tweets')

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.email == 'admin@mickle123.com'

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or IsAdmin().has_permission(request, view)

logger = logging.getLogger('tweets')
User = get_user_model()


class LikeToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk, format=None):
        tweet_qs = Tsubuyaki.objects.filter(pk=pk)
        message = "Not allowed"
        if request.user.is_authenticated:
            is_liked = Tsubuyaki.objects.like_toggle(request.user, tweet_qs.first())
            return Response({'liked': is_liked})
        return Response({"message":message}, status=400)



class RetweetAPIView(APIView):
    permission_classes =  [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        tweet_qs = Tsubuyaki.objects.filter(pk=pk)
        message = "Not allowed"
        if tweet_qs.exists() and tweet_qs.count() == 1:
            #if request.user.is_authenticated:
            new_tweet = Tsubuyaki.objects.retweet(request.user, tweet_qs.first())
            if new_tweet is not None:
                data = TweetModelSerializer(new_tweet).data
                return Response(data)
            message = "Cannot remickle the same in one day"
        return Response({"message":message}, status=400)

class PointsAPIView(generics.RetrieveAPIView):
    permission_classes =  [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = UserDisplaySerializer
    lookup_field = 'pk'

    def get_object(self):
        try:
            qs = Tsubuyaki.objects.filter(id=self.kwargs['tsubuyaki_id'])
            target = Tsubuyaki.objects.get(id=self.kwargs['tsubuyaki_id'])
            user = qs.values('user').first()["user"]
            points = qs.values('points').first()['points']
            content = qs.values('content').first()["content"]
            obj_1 = UserProfile.objects.filter(user=user).first()

            instance_2 = UserProfile.objects.get(user=self.request.user)
            obj_2 = UserProfile.objects.filter(user=self.request.user).first()

            total_1 = obj_1.points + points
            total_2 = obj_2.points- points

            data_1 = {'points': total_1}
            data_2 = {'points': total_2}

            update_serializer_1 = UserDisplaySerializer(obj_1,data=data_1,partial=True)
            update_serializer_2 = UserDisplaySerializer(obj_2,data=data_2, partial=True)

            if update_serializer_1.is_valid() and update_serializer_2.is_valid():# and update_serializer_2.is_valid():
                update_serializer_1.save()
                update_serializer_2.save()
                url_1 = "/tweet/" + str(self.kwargs['tsubuyaki_id']) + "/"
                logger.info(url_1)
                url_2 = "/" + str(self.request.user) + "/"
                logger.info(url_2)
                verb = self.kwargs['tsubuyaki_id']
                logger.info(verb)
                logger.info(content)
                notify.send(self.request.user, recipient=obj_1.user, verb="purchase", target=target)
            else:
                logger.info("Failed to save")
        except Exception as e:
            logger.info(e)
            raise Http404(e)

        return instance_2


class TweetCreateAPIView(generics.CreateAPIView):
    serializer_class = TweetModelSerializer_2
    permission_classes =  [permissions.IsAuthenticated]

    def perform_create(self,serializer):
        serializer.save(user=self.request.user)

class TweetDetailAPIView(generics.ListAPIView):
    queryset = Tsubuyaki.objects.all()
    serializer_class = TweetModelSerializer
    permission_classes =  [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get_queryset(self, *args, **kwargs):
        tweet_id = self.kwargs.get("pk")
        qs = Tsubuyaki.objects.filter(pk=tweet_id)
        if qs.exists() and qs.count() == 1:
            parent_obj = qs.first()
            qs1 = parent_obj.get_children()
            qs = (qs | qs1).distinct().extra(select={"parent_id_null": 'parent_id IS NULL'})
        return qs.order_by("-parent_id_null", '-timestamp')

class MickleAPIView(generics.ListAPIView):
    queryset = Tsubuyaki.objects.all()
    serializer_class = TweetModelSerializer
    permission_classes =  [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get_queryset(self, *args, **kwargs):
        user_id = self.kwargs.get("id")
        qs = Tsubuyaki.objects.filter(purchased_by=user_id)
        return qs.order_by('-timestamp')

class StockedMickleAPIView(generics.ListAPIView):
    queryset = Tsubuyaki.objects.all()
    serializer_class = TweetModelSerializer
    permission_classes =  [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get_queryset(self, *args, **kwargs):
        user_id = self.kwargs.get("id")
        qs = Tsubuyaki.objects.filter(liked=user_id)
        return qs.order_by('-timestamp')


class SearchTweetAPIView(generics.ListAPIView):
    queryset         = Tsubuyaki.objects.all().order_by("-timestamp")
    serializer_class = TweetModelSerializer
    pagination_class = StandardResultsPagination

    def get_serializer_context(self, *args, **kwargs):
        context = super(SearchTweetAPIView, self).get_serializer_context(*args, **kwargs)
        context['request'] = self.request
        return context

    def get_queryset(self, *args, **kwargs):
        qs    = self.queryset
        query = self.request.GET.get("q", None)
        if query is not None:
            qs = qs.filter(
                    Q(content__icontains=query) | #two underscore!! __ <-
                    Q(user__username__icontains=query)
                    )
        return qs


class TweetListAPIView(generics.ListAPIView):
    serializer_class = TweetModelSerializer
    pagination_class = StandardResultsPagination
    #serializer_class = UserDisplaySerializer
    # queryset = UserProfile.objects.all()

    def get_serializer_context(self, *args, **kwargs):
        context = super(TweetListAPIView, self).get_serializer_context(*args, **kwargs)
        context['request'] = self.request
        return context


    def get_queryset(self, *args, **kwargs):
        requested_user = self.kwargs.get("username") #the person trying to get the data thru this
        if requested_user:
            qs = Tsubuyaki.objects.filter(user__username=requested_user).order_by("-timestamp")
        else:
            im_following = self.request.user.profile.get_following()
            qs1 = Tsubuyaki.objects.filter(user__in=im_following)
            qs2 = Tsubuyaki.objects.filter(user=self.request.user)
            qs = (qs1 | qs2).distinct().order_by("-timestamp")

        query = self.request.GET.get("q", None)
        if query is not None:
            qs = qs.filter(
                    Q(content__icontains=query) | #two underscore!! __ <-
                    Q(user__username__icontains=query)
                    )
        return qs
