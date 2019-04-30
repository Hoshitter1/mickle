import re
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from .validators import validate_content
from django.urls import reverse
from django.utils import timezone
from hashtag.signals import parsed_hashtags
from django.core.validators import MaxValueValidator
from notifications.signals import notify
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger('tweets')
User = get_user_model()

class TweetManager(models.Manager):
    def retweet(self, user, parent_obj):
        if parent_obj.parent:
            og_parent = parent_obj.parent
        else:
            og_parent = parent_obj

        qs = self.get_queryset().filter(
            user=user,
            parent=og_parent,
            ).filter(
            timestamp__year=timezone.now().year,
            timestamp__month=timezone.now().month,
            timestamp__day=timezone.now().day,
            reply=False,
            )

        if qs.exists():
            return None
        obj = self.model(
            parent = og_parent,
            user   = user,
            content = parent_obj.content,
            )
        obj.save()
        parent_obj.remickled_by.add(user)
        try:
            if user != og_parent.user:
                notify.send(user, recipient=og_parent.user, verb="retweet",target=og_parent)
        except Exception as e:
            logger.info(e)
        return obj

    def like_toggle(self, user, tweet_obj):
        if user in tweet_obj.liked.all():
            is_liked = False
            tweet_obj.liked.remove(user)
        else:
            is_liked = True
            tweet_obj.liked.add(user)
            if user != tweet_obj.user:
                notify.send(user, recipient=tweet_obj.user, verb="like",target=tweet_obj)
        return is_liked

    def purchased_by_toggle(self, user, tweet_obj):
        if user in tweet_obj.purchased_by.all():
            is_purchased = False
        else:
            is_purchased = True
            tweet_obj.purchased_by.add(user)
        return is_purchased

class Tsubuyaki(models.Model):
    parent      = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title       = models.CharField(max_length=120,default='No title', validators=[validate_content])
    content     = models.CharField(max_length=620, validators=[validate_content])
    liked       = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked')
    reply       = models.BooleanField(verbose_name='Is a reply?', default=False)
    updated     = models.DateTimeField(auto_now=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    image       = models.ImageField(upload_to="static/Tsubuyaki/", blank=True)
    points      = models.PositiveIntegerField(default=0,validators=[MaxValueValidator(100),])
    purchased_by= models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,related_name='purchased_by')
    remickled_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='remickled')

    objects = TweetManager()

    def __str__(self):
        return str(self.content)

    def get_absolute_url(self):
        return reverse("tweet:detail", kwargs={"pk":self.pk})

    class Meta:
        ordering = ['-timestamp']

    def get_parent(self):
        the_parent = self
        if self.parent:
            the_parent = self.parent
        return the_parent

    def get_children(self):
        parent = self.get_parent()
        qs = Tsubuyaki.objects.filter(parent=parent)
        qs_parent = Tsubuyaki.objects.filter(pk=parent.pk)
        try:
            logger.info(qs.values('reply').first()["reply"])
            if qs.values('reply').first()["reply"] == True:
                return (qs | qs_parent)
            else:
                return qs_parent
        except Exception as e:
            logger.info(e)
            return  (qs | qs_parent)

def tweet_save_receiver(sender, instance, created, *args, **kwargs):

    if instance.reply == True:
        user_regex = r'@(?P<username>[\w.@+-]+)'
        usernames = re.search(user_regex, instance.content)
        username = re.match(user_regex, instance.content)
        description = instance.content.replace(username.group(),"")
        username = username.group().strip("@")
        username = User.objects.get(username__iexact=username)
        if instance.user != username:
            notify.send(instance.user, recipient=username, verb="reply",target=instance,description=description)

    if created and not instance.parent:
        user_regex = r'@(?P<username>[\w.@+-]+)'
        usernames = re.search(user_regex, instance.content)

        hash_regex = r'#(?P<hashtag>[\w\d-]+)'
        hashtags = re.findall(hash_regex, instance.content)
        parsed_hashtags.send(sender=instance.__class__, hashtag_list=hashtags)



post_save.connect(tweet_save_receiver, sender=Tsubuyaki)
