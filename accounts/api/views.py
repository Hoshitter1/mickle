from rest_framework import generics
from .serializers import UserDisplaySerializer
from accounts.models import UserProfile

class AccountListAPIView(generics.ListAPIView):
    serializer_class = UserDisplaySerializer

    def get_queryset(self, *args, **kwargs):
        return UserProfile.objects.all()
