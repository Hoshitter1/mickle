from django.utils.timesince import timesince
from django.urls import reverse_lazy
from rest_framework import serializers
from django.db.models import Q
#from accounts.api.serializers import UserDisplaySerializer
from tweets.models import Tsubuyaki
from accounts.models import UserProfile
import logging

logger = logging.getLogger('tweets')

class UserDisplaySerializer(serializers.ModelSerializer):
    queryset = UserProfile.objects.all()
    id = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'name',
            'follower_count',
            'url',
            'points',
            'image',
        ]

    def get_id(self,obj):
        qs = UserProfile.objects.filter(user__exact=obj)
        id = qs.values('id').first()["id"]
        return  id

    def get_user(self, obj):
        return str(obj)#obj.user.username) #idk why but you gotta set up this way

    def get_name(self, obj):
        qs = UserProfile.objects.filter(user__exact=obj)
        image = qs.values('name').first()["name"]
        return  image

    def get_follower_count(self, obj):
        return 0

    def get_url(self, obj):
        return reverse_lazy("profiles:detail", kwargs={"username": obj})

    def get_points(self, obj):
        qs = UserProfile.objects.filter(user__exact=obj)
        points = qs.values('points').first()["points"]
        return  points

    def get_image(self, obj):
        qs = UserProfile.objects.filter(user__exact=obj)
        image = qs.values('image').first()["image"]
        return  image

class ParentTweetModelSerializer(serializers.ModelSerializer):
    user = UserDisplaySerializer(read_only=True)
    date_display = serializers.SerializerMethodField()
    timesince = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    did_like = serializers.SerializerMethodField()
    purchase_count = serializers.SerializerMethodField()

    class Meta:
        model = Tsubuyaki
        fields = [
            'id',
            'user',
            'title',
            'content',
            'timestamp',
            'date_display',
            'timesince',
            'purchase_count',
            'likes',
            'did_like',
            'purchased_by',
            'points',
        ]

    def get_did_like(self, obj):
        request = self.context.get("request")
        try:
            user = request.user
            if user.is_authenticated:
                if user in obj.liked.all():
                    return True
        except:
            pass
        return False

    def get_purchase_count(self, obj):
        return obj.purchased_by.all().count()

    def get_likes(self, obj):
        return obj.liked.all().count()

    def get_date_display(self, obj):
        return obj.timestamp.strftime("%b %d, %Y at %I:%M %p")

    def get_timesince(self, obj):
        return timesince(obj.timestamp) + "ago"

class TweetModelSerializer(serializers.ModelSerializer):
    parent_id = serializers.CharField(write_only=True, required=False)
    user = UserDisplaySerializer(read_only=True)
    date_display = serializers.SerializerMethodField()
    timesince = serializers.SerializerMethodField()
    parent = ParentTweetModelSerializer(read_only=True)
    likes = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    did_like = serializers.SerializerMethodField()
    purchase_count = serializers.SerializerMethodField()
    did_remickle = serializers.SerializerMethodField()
    remickles = serializers.SerializerMethodField()

    class Meta:
        model = Tsubuyaki
        fields = [
            'parent_id',
            'id',
            'user',
            'title',
            'content',
            'timestamp',
            'date_display',
            'timesince',
            'parent',
            'likes',
            'did_like',
            'purchase_count',
            'reply',
            'image',
            'points',
            'purchased_by',
            'remickled_by',
            'did_remickle',
            'remickles',
        ]
        #read_only_fields = ['reply']

    def get_content(self,obj):
        request = self.context.get("request")
        try:
            user = request.user
            if obj.points > 0:
                if user.is_authenticated:
                    if user in obj.purchased_by.all() or user == obj.user:
                        return obj.content
                    else:
                        return "Please purchase the mickle to see the content"
                else:
                    return "Please login and purchase the mickle to see the content"
            else:
                return obj.content
        except:
            return "an error occured"

    def get_did_like(self, obj):
        request = self.context.get("request")
        try:
            user = request.user
            if user.is_authenticated:
                if user in obj.liked.all():
                    return True
        except:
            pass
        return False

    def get_did_remickle(self, obj):
        request = self.context.get("request")
        try:
            user = request.user
            if user.is_authenticated:
                if user in obj.remickled_by.all():
                    return True
        except:
            pass
        return False

    def get_likes(self, obj):
        return obj.liked.all().count()

    def get_remickles(self, obj):
        return obj.remickled_by.all().count()

    def get_purchase_count(self, obj):
        return obj.purchased_by.all().count()

    def get_date_display(self, obj):
        return obj.timestamp.strftime("%b %d, %Y at %I:%M %p")

    def get_timesince(self, obj):
        logger.info(timesince(obj.timestamp))
        return timesince(obj.timestamp) + " ago"

class TweetModelSerializer_2(serializers.ModelSerializer):
    parent_id = serializers.CharField(write_only=True, required=False)
    user = UserDisplaySerializer(read_only=True)
    date_display = serializers.SerializerMethodField()
    timesince = serializers.SerializerMethodField()
    parent = ParentTweetModelSerializer(read_only=True)
    likes = serializers.SerializerMethodField()
    did_like = serializers.SerializerMethodField()
    purchase_count = serializers.SerializerMethodField()
    did_remickle = serializers.SerializerMethodField()
    remickles = serializers.SerializerMethodField()
    purchased_by = serializers.SerializerMethodField(read_only=True)
    remickled_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tsubuyaki
        fields = [
            'parent_id',
            'id',
            'user',
            'title',
            'content',
            'timestamp',
            'date_display',
            'timesince',
            'parent',
            'likes',
            'did_like',
            'purchase_count',
            'reply',
            'image',
            'points',
            'purchased_by',
            'remickled_by',
            'did_remickle',
            'remickles',
        ]
        #read_only_fields = ['reply']

    def get_did_like(self, obj):
        request = self.context.get("request")
        try:
            user = request.user
            if user.is_authenticated:
                if user in obj.liked.all():
                    return True
        except:
            pass
        return False

    def get_did_remickle(self, obj):
        request = self.context.get("request")
        try:
            user = request.user
            if user.is_authenticated:
                if user in obj.remickled_by.all():
                    return True
        except:
            pass
        return False

    def get_likes(self, obj):
        return obj.liked.all().count()

    def get_remickles(self, obj):
        return obj.remickled_by.all().count()

    def get_purchase_count(self, obj):
        return obj.purchased_by.all().count()

    def get_date_display(self, obj):
        return obj.timestamp.strftime("%b %d, %Y at %I:%M %p")

    def get_timesince(self, obj):
        return timesince(obj.timestamp) + " ago"

    def get_purchased_by(self, obj):
        return None

    def get_remickled_by(self, obj):
        return None
