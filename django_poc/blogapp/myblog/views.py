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


# @user_passes_test(superuser_only, login_url='login')
def profile_view(request, user_id):
    if user_id:
        user = User.objects.get(id=user_id)
        userProfile = UserProfile.objects.get(user.id)
        return render(request, 'myblog/profile.html', {'user': user, 'userProfile': userProfile})
