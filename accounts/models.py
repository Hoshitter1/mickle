from django.conf import settings
from django.db import models
from django.urls import reverse_lazy
from django.db.models.signals import post_save
# Create your models here.
import logging
from django.contrib.auth import get_user_model
from tweets.models import Tsubuyaki
from notifications.signals import notify

logger = logging.getLogger('tweets')
User = get_user_model()

def default_user():
    default_user = User.objects.get_or_create(username='admin')
    return default_user

class Payment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    purchase_id = models.IntegerField(unique=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    points = models.PositiveIntegerField(null=True)

class Activate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=255, unique=True)
    expiration_date = models.DateTimeField(blank=True, null=True)

class UserProfileManager(models.Manager):
    use_for_related_fields = True

    def all(self):
        qs = self.get_queryset().all()
        try:
            if self.instance:
                qs = qs.exclude(user=self.instance)
        except:
            pass
        return qs

    def toggle_follow(self, user, to_toggle_user):
        user_profile, created = UserProfile.objects.get_or_create(user=user) #(user_obj, true)
        if to_toggle_user in user_profile.following.all():
            user_profile.following.remove(to_toggle_user)
            added = False
        else:
            user_profile.following.add(to_toggle_user)
            notify.send(user, recipient=to_toggle_user, verb="follow")
            added = True
        return added

    def toggle_tsubuyaki(self, user, to_toggle_purchased):
        user_profile, created = UserProfile.objects.get_or_create(user=user) #(user_obj, true)
        if to_toggle_purchased in user_profile.purchased_tsubuyaki.all():
            added = False
        else:
            user_profile.purchased_tsubuyaki.add(to_toggle_purchased)
            added = True
        return added

    def is_following(self, user, followed_by_user):
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            return False
        if followed_by_user in user_profile.following.all():
            return True
        return False

    def recommended(self, user, limit_to=10):
        profile = user.profile
        following = profile.following.all()
        following = profile.get_following()
        qs = self.get_queryset().exclude(user__in=following).exclude(id=profile.id).order_by("?")[:limit_to]
        return qs


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=50,default='(´･ω･)')
    description = models.CharField(max_length=250,default="Lah!")
    following = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,related_name='followed_by',default='1')
    purchased_tsubuyaki = models.ManyToManyField(Tsubuyaki, blank=True,related_name='purchased')
    image = models.ImageField(upload_to="static/profile/", default="no_img")
    points = models.PositiveIntegerField(default=50)

    objects = UserProfileManager()
        #user.profile.following -- users I follow
        #user.followed_by -- users that follow me -- reverse relationship

    def __str__(self): #title of the user on admin page
        return str(self.user)

    def get_following(self):
        users = self.following.all()
        return users.exclude(username=self.user)

    def get_follow_url(self):
        return reverse_lazy("profiles:follow", kwargs={"username":self.user.username})

    def get_absolute_url(self):
        return reverse_lazy("profiles:detail", kwargs={"username":self.user.username})


    # def save(self, *args, **kwargs):
    #     try:
    #         original_profile = UserProfile.objects.get(pk=self.pk)
    #         if original_profile.image:
    #             original_profile.image.delete(save=False)
    #     except self.DoesNotExist:
    #         logger.info(self)
    #         pass
    #     super(UserProfile, self).save(*args, **kwargs)



# def my_handler(sender, instance, created, **kwargs):
#     logger.info(instance)
#     logger.info(sender)
#     logger.info(created)
#     #user = User.objects.filter(username__exact=instance)
#     #user_update = UserProfile.objects.get_or_create(user=user)
#     notify.send(instance,verb="was saved")
# post_save.connect(my_handler, sender=UserProfile)


 # ubuntu = User.objects.first()
 # User.objects.get_or_create() #(user_obj, true/false)
 # ubuntu.save()


def post_save_user_receiver(sender, instance, created, *args, **kwargs):
    if created:
        new_profile = UserProfile.objects.get_or_create(user=instance)
        # logger.info(new_profile)
        # user_profile, created = UserProfile.objects.get_or_create(user="admin")
        # user_profile.following.add(new_profile)
        # celery + redis
        # deferred tasks such as email
post_save.connect(post_save_user_receiver, sender=settings.AUTH_USER_MODEL)
