from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, loader
from blogapp.forms import SignupForm
import random, sha, re
from django.contrib.auth.decorators import user_passes_test
from myblog.models import UserProfile


# Create your views here.

def superuser_only(user):
    return (user.is_authenticated() and user.is_superuser)

def home_view(request):
    return render(request, 'home.html')

def signup_view(request):

    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():

            first_name = request.POST.get('first_name', None)
            last_name = request.POST.get('last_name', None)
            email = request.POST.get('email', None)
            password = request.POST.get('password', None)
            confirm_password = request.POST.get('confirm_password', None)

            email_error = ""
            password_error = ""

            if email_error == "" and password_error == "":
                new_user = User.objects.create_user(
                    username=email,
                    password=password,
                    email=email,
                )

                new_user.is_active = False
                new_user.first_name = first_name
                new_user.last_name = last_name
                new_user.save()

                # Generate a salted SHA1 hash to use as a key.
                salt = sha.new(str(random.random())).hexdigest()[:5]
                activation_key = sha.new(salt + new_user.email).hexdigest()

                userprofile = UserProfile()
                userprofile.user_id = new_user.id
                userprofile.activation_token = activation_key
                userprofile.save()

                current_domain = settings.SITE_URL
                subject = "Activate your new account at %s" % current_domain
                message_template = loader.get_template('email_content/activation.txt')
                message_context = Context({
                    'user_name': new_user.first_name + ' ' + new_user.last_name,
                    'site_url': 'http://%s/' % current_domain,
                    'activation_key': activation_key
                })
                message = message_template.render(message_context)
                send_mail(subject, message, 'no-reply@gmail.com', [new_user.email])

                success_message = "You've been successfully register with Tweet Me. Check your email address for email confirmation"
                messages.add_message(request, messages.INFO, success_message)
                return HttpResponseRedirect(reverse('home'))
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def activate_user(request, activation_token):
    if activation_token:
        try:
            user_profile = UserProfile.objects.get(activation_token=activation_token)
        except UserProfile.DoesNotExist:
            messages.add_message(request, messages.INFO, 'Invalid link or Token has been expired!')
            return HttpResponseRedirect(reverse('home'))

        if user_profile.activation_token:
            user = user_profile.user

            if not user.is_active:
                user.is_active = True
                user.save()
                success_message = "Congratulations.. Now you can Tweet happily..!!!"
                messages.add_message(request, messages.INFO, success_message)
                return HttpResponseRedirect(reverse('home'))
            else:
                messages.add_message(request, messages.INFO, 'Your account is already active!')
                return HttpResponseRedirect(reverse('home'))

    messages.add_message(request, messages.INFO, 'Token doesn\'t exist!')
    return HttpResponseRedirect(reverse('home'))
