from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect, Http404
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.template.loader import get_template
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import (
                            DetailView,
                            ListView,
                            CreateView,
                            UpdateView,
                            DeleteView,
                            TemplateView
                            )
from django.views.generic.edit import FormView
from django.db.models import Q
# Create your views here.
from .forms import (UserRegisterForm,
                    ProfileImage,
                    PasswordUpdate,
                    ProfileName,
                    EmailUpdate,
                    )
from .models import UserProfile, Activate, Payment
import logging
from django.contrib import messages
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
#from users.backends import EmailModelBackend
from django.contrib.auth import login as auth_login
from .token_manager import create_expiration_date, create_key
import datetime
from pytz import timezone as tmz
from django.utils import timezone
from django.urls import reverse_lazy
from tweets.models import Tsubuyaki
from django.contrib.auth.views import PasswordChangeView
from coingate_api import CoingateAPI, api_error
import secrets
from notifications.signals import notify
from django.conf import settings
import urllib, urllib.request, urllib.parse, json

logger = logging.getLogger('tweets')

User = get_user_model()

auth_token = settings.AUTH_TOKEN
sand_auth_token = settings.SAND_AUTH_TOKEN


class UserRegisterView(FormView):
    template_name = 'accounts/user_register_form.html'
    form_class = UserRegisterForm
    success_url = '/create_done'

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        new_user = User.objects.create(username=username, email=email)
        new_user.set_password(password)
        new_user.is_active = False
        new_user.save()

        # uuid => create random str
        activate_key = create_key()
        expiration_date = create_expiration_date()
        # crate a record that is valid for an hour
        activate_instance = Activate(user=new_user, key=activate_key, expiration_date=expiration_date)
        activate_instance.save()

        #get domain
        current_site = get_current_site(self.request)
        domain = current_site.domain
        domain = "mickle123.com"

        message_template = get_template('mailtemplate/new/message.txt')
        uid = force_text(urlsafe_base64_encode(force_bytes(activate_key)))

        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'uid': uid,
            'user': username,
        }

        # send email
        subject = 'Welocome to Mickle'
        message = message_template.render(context)
        from_email = settings.EMAIL_HOST_USER
        to = [email]
        send_mail(subject, message, from_email, to)
        messages.success(self.request, "Hi {} I've sent you an email to validate your email address".format(username))

        #result = super().form_valid(form)
        #return result
        return super(UserRegisterView, self).form_valid(form)

    def recaptha(req):
        recaptcha_response = req.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': '6LcxfpQUAAAAABIZMN6p06xBmsKONQeuJvNBTCIo',
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode('utf-8')
        req = urllib.request.Request(url, data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        return result

class CreateDoneView(TemplateView):
    template_name = "accounts/create_done.html"

class CreateCompleteView(TemplateView):
    template_name = 'accounts/create_complete.html'

    def get(self, request, **kwargs):
        uidb64 = kwargs.get("uidb64")
        try:
            key = force_text(urlsafe_base64_decode(uidb64))
            activate = get_object_or_404(Activate, key=key)
            user = activate.user
            expiration_date = activate.expiration_date + datetime.timedelta(hours=9)
            t_now = datetime.datetime.now(tmz('UTC'))

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and not user.is_active and t_now <= expiration_date:
            context = super(CreateCompleteView, self).get_context_data(**kwargs)
            user.is_active = True
            user.save()
            #user.backend = 'users.backends.EmailModelBackend'
            auth_login(request, user)
            response_message = "Congrats!! You have succefuly registred!!"
            context["message"] = response_message
            # delete token
            Activate.objects.filter(key=key).delete()
            toggle_user = get_object_or_404(User, username__iexact="admin")
            if request.user.is_authenticated:
                is_following = UserProfile.objects.toggle_follow(request.user, toggle_user)
            return render(self.request, self.template_name, context)
        else:
            # delete token
            Activate.objects.filter(key=key).delete()
            if user :
                # delete tentative user data
                User.objects.filter(username=user.username).delete()
            return render(request, 'accounts/create_failed.html')



class UserDetailView(DetailView):
    template_name = 'accounts/user_detail.html'
    queryset = UserProfile.objects.all()

    def get_object(self):
        return get_object_or_404(User, username__iexact=self.kwargs.get("username"))

    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailView, self).get_context_data(*args, **kwargs)
        user = self.kwargs.get("username")
        following = UserProfile.objects.is_following(self.request.user, self.get_object())
        obj = get_object_or_404(UserProfile,user=self.get_object())
        context['image'] = obj.image
        if context['image'] == "no_img":
            context['image'] ="static/Hiyoko.png"
        context['user'] = obj.user
        context['name'] = obj.name
        context['following'] = following
        context['recommended'] = UserProfile.objects.recommended(self.request.user)
        qs = UserProfile.objects.filter(user__exact=self.request.user)
        qs_user = User.objects.filter(username=self.request.user)
        context['user_id_1'] = qs_user.values('id').first()["id"]
        context['user_id_2'] =qs.values('id').first()["id"]
        return context

class UserFollowView(View):
    def get(self, request, username, *args, **kwargs):
        toggle_user = get_object_or_404(User, username__iexact=username)

        if request.user.is_authenticated:
            is_following = UserProfile.objects.toggle_follow(request.user, toggle_user)
        return redirect("profiles:detail", username=username) #HttpResponseRedirect()


class Purchase_tsubuyaki(View):
    def get(self, request, id, *args, **kwargs):
        toggle_purchased = get_object_or_404(Tsubuyaki, id__iexact=id)
        if request.user.is_authenticated:
            is_purchased = UserProfile.objects.toggle_tsubuyaki(request.user, toggle_purchased)
            is_tsubuyakied = Tsubuyaki.objects.purchased_by_toggle(request.user, toggle_purchased)
        return redirect("tweet:detail", pk=id)

class UserPointsView(DetailView):
    template_name = 'accounts/user_points.html'
    queryset = User.objects.all()
    def get_object(self):
        return get_object_or_404(User, username__iexact=self.kwargs.get("username"))

    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailView, self).get_context_data(*args, **kwargs)
        following = UserProfile.objects.is_following(self.request.user, self.get_object())
        context['following'] = following
        context['recommended'] = UserProfile.objects.recommended(self.request.user)
        return context


class model_form_upload(UpdateView):
    form_class = ProfileImage
    success_url = "/"

    def get_object(self):
        user = get_object_or_404(User, username__iexact=self.kwargs.get("username"))
        return get_object_or_404(UserProfile,user=user)




class SettingView(TemplateView):
    template_name = "accounts/setting.html"

    def get_object(self):
        return get_object_or_404(User, username__iexact=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super(SettingView, self).get_context_data(*args, **kwargs)
        qs = User.objects.filter(username__exact=self.request.user)
        context['user_id'] = qs.values('pk').first()["pk"]
        return context

class EmailUpdate(UpdateView):
    form_class = EmailUpdate
    template_name = 'accounts/email_update.html'
    success_url = "/"

    def get_object(self):
        return get_object_or_404(User, username__iexact=self.kwargs.get("username"))

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        return super(EmailUpdate, self).form_valid(form)

class PasswordUpdate(PasswordChangeView):
    form_class = PasswordUpdate
    template_name = 'accounts/password_update.html'
    success_url = "/"



class NameUpdate(UpdateView):
    form_class = ProfileName
    success_url = "/"

    def get_object(self):
        user = get_object_or_404(User, username__iexact=self.kwargs.get("username"))
        return get_object_or_404(UserProfile,user=user)

class UserDeleteView(LoginRequiredMixin,DeleteView):
    model = User
    template_name = "accounts/delete_confirm.html"
    success_url = "/"

    def get_queryset(self):
        return self.model.objects.filter(pk=self.kwargs.get("pk"))

class PontsView(TemplateView):
    template_name = "accounts/points.html"
    def get_object(self):
        return get_object_or_404(User, username__iexact=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super(PontsView, self).get_context_data(*args, **kwargs)
        qs = User.objects.filter(username__exact=self.request.user)
        context['user_id'] = qs.values('pk').first()["pk"]

        api = CoingateAPI(auth_token=auth_token, environment='live')
        BTC_rate = api.exchange_rate(from_='BTC', to='JPY')
        USD_rate = api.exchange_rate(from_='USD', to='JPY')
        context['BTC_rate'] = round(1/10000000*BTC_rate,4)
        context['BTC_min_points'] = round(1/1000*BTC_rate) #0.001BTC is the min of CoinGate
        context['USD_rate'] = round(1/USD_rate,3)
        return context

class NotificationView(ListView):
    template_name = "accounts/notification.html"

    def get_queryset(self, *args, **kwargs): #sort data out of database
        qs = User.objects.get(username__exact=self.request.user)
        qs = qs.notifications.all()
        return qs

    # def get_context_data(self, *args, **kwargs):
    #     context = super(NotificationView, self).get_context_data(*args, **kwargs)
    #     qs = User.objects.get(username__exact=self.request.user)
    #     context['unread'] =  qs.notifications.unread()
    #     context['unsent'] =  qs.notifications.unsent()
    #     context['sent'] =  qs.notifications.sent()
    #     context['read'] =  qs.notifications.read()
    #     # qs.notifications.mark_all_as_read()
    #     return context



class MickleView(TemplateView):
    template_name = "accounts/mickles.html"

    def get_context_data(self, *args, **kwargs): #add data not out of database or another mdoel
        context = super(MickleView, self).get_context_data(*args, **kwargs) #inherit data from class
        qs_user_1 = User.objects.filter(username=self.request.user)
        qs_user_2 = UserProfile.objects.filter(user=self.request.user)
        context['user_id_1'] =qs_user_1.values('id').first()["id"]
        context['user_id_2'] =qs_user_2.values('id').first()["id"]
        return context

class StockedMickleView(TemplateView):
    template_name = "accounts/stocked_mickles.html"

    def get_context_data(self, *args, **kwargs): #add data not out of database or another mdoel
        context = super(StockedMickleView, self).get_context_data(*args, **kwargs) #inherit data from class
        qs_user_1 = User.objects.filter(username=self.request.user)
        qs_user_2 = UserProfile.objects.filter(user=self.request.user)
        context['user_id_1'] =qs_user_1.values('id').first()["id"]
        context['user_id_2'] =qs_user_2.values('id').first()["id"]
        return context


def PurchasePointsView(request):
    try:
        if request.method == "POST":
            points   = request.POST.get("points")
            #currency = request.POST.get("currency")
            user =  User.objects.get(username=request.user)
            created_date = datetime.datetime.now(tmz('UTC'))
            order_id = str(request.user) + "_" +str(datetime.datetime.now(tmz('UTC')))
            token = secrets.token_hex()
            token = str(token)
            url = "http://mickle123.com/setting/" + token + "/points/result/"
            url_2 = "http://mickle123.com/setting/" + token + "/points/cancel/"

            api = CoingateAPI(auth_token=auth_token, environment='live')
            rate = api.exchange_rate(from_='BTC', to='JPY')
            crypto_amount = float(points)/rate
            point_rate = 1/rate
            description = str('1point={0}BTC'.format(point_rate))
            result = api.create_order(
                                crypto_amount,
                                "BTC",
                                "do_not_convert",
                                order_id=order_id,
                                title="Purchase points on mickle",
                                description=description,
                                token=token,
                                callback_url=url,
                                cancel_url=url_2,
                                success_url=url,
                                )
            Payment.objects.filter(user=request.user).delete()
            payment_instance = Payment(user=request.user, token=token, purchase_id=result['id'], created_date=created_date, points=points)
            payment_instance.save()
            return HttpResponseRedirect(result['payment_url'])
        else:
            raise Http404("request.method is not POST")
    except Exception as e:
        logger.info(e)
        raise Http404("An error occured")

class purchase_successView(LoginRequiredMixin,TemplateView):
    template_name = "accounts/success.html"

    def get(self, request, **kwargs):
        try:
            api = CoingateAPI(auth_token=auth_token, environment='live')
            qs = Payment.objects.filter(user=request.user)
            id = qs.values('purchase_id').first()["purchase_id"]
            result = api.checkout(id)# if there were no such an order, it would return error
            if result['status'] == 'paid':
                user_obj = UserProfile.objects.filter(user=self.request.user).first()
                points_original = user_obj.points
                points_add = qs.values('points').first()["points"]
                points = points_original + points_add
                user_obj.points = points
                user_obj.save()
                Payment.objects.filter(user=request.user).delete()
            else:
                logger.info(result)
            return render(self.request, self.template_name)
        except api_error.APIError as e:
            logger.info(e)
            return render(self.request,'accounts/fail.html')

class CancelView(LoginRequiredMixin,TemplateView):
    template_name = "accounts/cancel.html"


        # try:
        #     key = force_text(urlsafe_base64_decode(uidb64))
        #     activate = get_object_or_404(Activate, key=key)
        #     user = activate.user
        #     expiration_date = activate.expiration_date + datetime.timedelta(hours=9)
        #     t_now = datetime.datetime.now(tmz('UTC'))
        #
        # except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        #     user = None
        #
        # if user and not user.is_active and t_now <= expiration_date:
        #     context = super(CreateCompleteView, self).get_context_data(**kwargs)
        #     user.is_active = True
        #     user.save()
        #     #user.backend = 'users.backends.EmailModelBackend'
        #     auth_login(request, user)
        #     response_message = "Congrats!! You have succefuly registred!!"
        #     context["message"] = response_message
        #     # delete token
        #     Activate.objects.filter(key=key).delete()
        #     return render(self.request, self.template_name, context)
        # else:
        #     # delete token
        #     Activate.objects.filter(key=key).delete()
        #     if user :
        #         # delete tentative user data
        #         User.objects.filter(username=user.username).delete()
        #     return render(request, 'accounts/create_failed.html')
# result = api.checkout("155209", pay_currency='BTC') logger.info(result)
