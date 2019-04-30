from django.contrib import admin

# Register your models here.
from .models import Tsubuyaki

from .forms import TweetModelForm


class TweetModelAdmin(admin.ModelAdmin):
    #form = TweetModelForm
    class Meta:
        model = Tsubuyaki

admin.site.register(Tsubuyaki, TweetModelAdmin)

#admin.site.register(Tsubuyaki)
