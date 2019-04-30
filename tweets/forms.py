from django import forms
from .models import Tsubuyaki
#from accounts.models import UserProfile

class TweetModelForm(forms.ModelForm):
    title       = forms.CharField(label='', required=False,widget=forms.TextInput(attrs={'placeholder': "your title", "class":"form-control", "rows":"1"}))
    content     = forms.CharField(label='', required=True,widget=forms.Textarea(attrs={'placeholder': "your message", "class":"form-control","rows":"5"}))
    image       = forms.ImageField(label="", required=False, widget=forms.FileInput(attrs={"accept":"image/*", "class":"form-control-file", "style":"display:none"}))
    points      = forms.IntegerField(label="", widget=forms.DateInput(attrs={"class":"form-control", "type":"number", "value":"0", "min":"0", "max":"100"}))
    class Meta:
        model = Tsubuyaki
        fields = [
            "title",
            "content",
            "image",
            "points",
        ]

# class UserImage(forms.ModelForm):
#     #image = forms.ImageField()
#     class Meta:
#         model = UserProfile
#         fields = [
#             "image"
#         ]
