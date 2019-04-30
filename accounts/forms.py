from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm

User = get_user_model()

class UserRegisterForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError("Password must match")
        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__icontains=username).exists():
            raise forms.ValidationError("This username is taken")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__icontains=email).exists():
            raise forms.ValidationError("This email is already registered")
        return email

# class ForgetPasswordForm(PasswordResetForm):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['email'].widget.attrs['class'] = 'form-control'
#         self.fields['email'].widget.attrs['placeholder'] = 'email adress'
#
#
# class ChangePasswordForm(PasswordChangeForm):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['new_password1'].widget.attrs['class'] = 'form-control'
#         self.fields['new_password2'].widget.attrs['class'] = 'form-control'
#         self.fields['old_password'].widget.attrs['class'] = 'form-control'
#
#
# class PasswordConfirmForm(SetPasswordForm):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['new_password1'].widget.attrs['class'] = 'form-control'
#         self.fields['new_password1'].widget.attrs['placeholder'] = 'new password'
#         self.fields['new_password2'].widget.attrs['class'] = 'form-control'
#         self.fields['new_password2'].widget.attrs['placeholder'] = 'new password(again)'

class ProfileName(forms.ModelForm):
    name = forms.CharField()
    class Meta:
        model = UserProfile
        fields = [
                'name',
                ]

class ProfileImage(forms.ModelForm):
    image = forms.ImageField(label='')
    class Meta:
        model = UserProfile
        fields = [
                'image',
                ]

class EmailUpdate(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = [
                'email',
                ]
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__icontains=email).exists():
            raise forms.ValidationError("This email is already registered")
        return email


class PasswordUpdate(PasswordChangeForm):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'




    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.fields.values():
    #         field.widget.attrs['class'] = 'form-control'
