from django.shortcuts import render
from django.views import View
from accounts.models import UserProfile
from django.contrib.auth import get_user_model

from .models import HashTag
User = get_user_model()

class HashTagView(View):
    def get(self, request, hashtag, *args, **kwargs):
        obj, created = HashTag.objects.get_or_create(tag=hashtag)
        qs_1 = User.objects.filter(username=self.request.user)
        qs_2 = UserProfile.objects.filter(user=self.request.user)
        context = { "obj":obj,
                    "user_id_1": qs_1.values('id').first()["id"],
                    "user_id_2": qs_2.values('id').first()["id"],
                    }
        return render(request, 'hashtags/tag_view.html', context)
