from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, loader
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from blogapp.forms import UserProfileForm, UploadUserPicForm, PostForm
import random, sha, re, os
from django.contrib.auth.decorators import user_passes_test
from myblog.models import UserProfile, Post


# Create your views here.

def superuser_only(user):
    return (user.is_authenticated() and user.is_superuser)


def user_only(user):
    return (user.is_authenticated())


@user_passes_test(user_only, login_url='login')
def profile_view(request):
    userProfile = UserProfile.objects.get(user_id=request.user.id)
    if not userProfile.photo:
        userProfile.photo = 'default.png'
    return render(request, 'myblog/profile.html', {'userProfile': userProfile})


@user_passes_test(user_only, login_url='login')
def edit_profile(request):

    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.user, request.POST)

        if user_profile_form.is_valid():

            user_data = {
                'first_name': request.POST.get('first_name', None),
                'last_name': request.POST.get('last_name', None),
                'email': request.POST.get('email', None),
            }

            user_profile_data = {
                'address': request.POST.get('address', None),
                'phone_number': request.POST.get('phone_number', None),
                'about_me': request.POST.get('about_me', None),
            }

            user_data = User.objects.filter(pk=request.user.id).update(**user_data)
            user_profile_data = UserProfile.objects.filter(user_id=request.user.id).update(**user_profile_data)
            return HttpResponseRedirect('/myblog/profile')

    else:
        user_data = get_object_or_404(User, id=request.user.id)
        user_profile = get_object_or_404(UserProfile, user_id=request.user.id)

        userProfileData = {
            'first_name': user_data.first_name,
            'last_name': user_data.last_name,
            'email': user_data.email,
            'phone_number': user_profile.phone_number,
            'address': user_profile.address,
            'about_me': user_profile.about_me,
            'photo': user_profile.photo,

        }
        user_profile_form = UserProfileForm(request.user, initial=userProfileData)

    return render(request, 'myblog/edit_profile.html', {'form': user_profile_form})


def upload_pic(request):
    if request.method == 'POST':
        form = UploadUserPicForm(request.POST, request.FILES)
        files = request.FILES.get('user_pic', None)
        if files:
            path = default_storage.save(settings.USER_IMAGE_PATH + str(files.name), ContentFile(files.read()))
            tmp_file_path = os.path.join(settings.USER_IMAGE_PATH, path)
            photo = files.name
            UserProfile.objects.filter(user_id=request.user.id).update(photo=photo)
        else:
            success_message = "Something has went wrong, please try again."
            messages.add_message(request, messages.INFO, success_message)
            return HttpResponseRedirect(reverse('/myblog/profile'))
    else:
        form = UploadUserPicForm()
    return HttpResponseRedirect('/myblog/profile')


def add_post(request):

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            user = User.objects.get(id=request.user.id)
            blog_post = Post()
            blog_post.title = request.POST.get('title', None)
            blog_post.content = request.POST.get('body', None)
            blog_post.tags = request.POST.get('tags', None)
            blog_post.status = request.POST.get('status', None)
            blog_post.rating = 0
            blog_post.slug = slugify(request.POST.get('title', None))
            blog_post.userid = user
            blog_post.save()

            success_message = "Post added successfully"

            messages.add_message(request, messages.INFO, success_message)
            return HttpResponseRedirect(reverse('home'))
    else:
        form = PostForm()

    return render(request, 'myblog/add_post.html', {'form': form})


def edit_post(request):
    id = request.GET.get('id', None)

    if id is not None:
        post = get_object_or_404(Post, id=id)
    else:
        post = None

    postdata = {'title': post.title,
                'body': post.content,
                'tags': post.tags,
                'status': post.status}

    if request.method == 'POST':
        postform = PostForm(request.POST)

        if postform.is_valid:

            post_dict = {
                'title': request.POST.get('title', None),
                'content': request.POST.get('body', None),
                'tags': request.POST.get('tags', None),
                'status': request.POST.get('tags', None),
            }

            Post.objects.filter(id=id).update(**post_dict)

            success_message = "Post updated successfully"

            messages.add_message(request, messages.INFO, success_message)
            return HttpResponseRedirect(reverse('home'))

    else:
        postform = PostForm(initial=postdata)

    return render(request, 'myblog/edit_post.html', {'form': postform})