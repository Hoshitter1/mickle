from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from rest_framework import serializers
from accounts.models import UserProfile
import logging

logger = logging.getLogger('tweets')


class UserDisplaySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    # points = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'follower_count',
            'url',
            'points',
            #'email',
        ]

    def get_user(self, obj):
        return str(obj)#obj.user.username) #idk why but you gotta set up this way

    def get_follower_count(self, obj):
        return 0

    def get_url(self, obj):
        return reverse_lazy("profiles:detail", kwargs={"username": obj})

    # def get_points(self, obj):
    #     logger.info(obj.points)
    #     return  obj.points
