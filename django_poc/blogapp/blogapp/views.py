from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.db.models import Q
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.template import Context, loader
from blogapp.forms import UserForm, ChangePasswordForm
from django.views.decorators.csrf import csrf_exempt
import random, sha, re, datetime
from django.contrib.auth.decorators import user_passes_test
from myblog.models import UserProfile, Post
import nltk
from nltk.tag import pos_tag, map_tag

# Create your views here.

def superuser_only(user):
    return (user.is_authenticated() and user.is_superuser)


def user_only(user):
    return (user.is_authenticated())


def get_tags(content):
    text = nltk.word_tokenize(content)
    post_tagged = pos_tag(text)
    get_tags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in post_tagged]
    return set(get_tags)


@csrf_exempt
def home_view(request):

    searchType = request.POST.get('search_type', None) if request.POST.get('search_type', None) else ''
    searchText = request.POST.get('search_text', None) if request.POST.get('search_text', None) else ''

    from_date = request.POST.get('from_date', None) + ' 00:00:00' if request.POST.get('from_date', None) else ''
    to_date = request.POST.get('to_date', None) + ' 23:59:59' if request.POST.get('to_date', None) else ''

    if searchType:
        if searchType == "author":
            allUserData = User.objects.filter(Q(first_name__icontains=searchText) | Q(last_name__icontains=searchText), is_active=1)
            user_ids = []
            for user in allUserData:
                user_ids.append(user.id)
            allPost = Post.objects.filter(status='publish', userid_id__in=user_ids).order_by('-created')
        else:
            if not searchType == "date":
                searchField = str(searchType) + str('__icontains')
                allPost = Post.objects.filter(status='publish', **{searchField: searchText}).order_by('-created')
            else:
                allPost = Post.objects.filter(status='publish', created__range=(from_date, to_date)).order_by('-created')
    else:
        allPost = Post.objects.filter(status='publish').order_by('-created')

    paginator = Paginator(allPost, 10)
    page = request.GET.get('page')

    try:
        post_data = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        post_data = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        post_data = paginator.page(paginator.num_pages)

    user_blog_data_list = []
    for each in post_data:
        user_blog_data = {}
        try:
            user_blog_data['post_info'] = each
            user_blog_data['post_info'].tags = get_tags(each.content)
            user_blog_data['user_obj'] = User.objects.get(id=each.userid.id)
            user_blog_data['user_profile'] = UserProfile.objects.get(user_id=each.userid.id)
            if not user_blog_data['user_profile'].photo:
                user_blog_data['user_profile'].photo = settings.USER_IMAGE_VIEW_PATH + 'default.png'
        except:
            return render(request, 'home.html', 'Error : Object does not exist')
        user_blog_data_list.append(user_blog_data)
    if request.user.id:
        userprofile = UserProfile.objects.get(user_id=request.user.id)
    else:
        userprofile = None

    user_dict = {
        'userprofile': userprofile,
        'blog_post': user_blog_data_list,
        'paginate_data': post_data,
        'search_text': searchText,
        'search_type': searchType,
        'from_date': request.POST.get('from_date'),
        'to_date': request.POST.get('to_date')
    }
    return render(request, 'home.html', user_dict)


def custom_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    else:
        return login(request)


def signup_view(request):

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'POST':
        form = UserForm(request.POST)

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
        form = UserForm()

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


@user_passes_test(user_only, login_url='login')
def reset_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        users = request.user
        users.set_password(request.POST.get('password', None))
        if form.is_valid():
            user_data = {
                'password': users.password,
            }
            user_data = User.objects.filter(pk=request.user.id).update(**user_data)
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect('/myblog/profile')

    else:

        form = ChangePasswordForm(user=request.user)

    return render(request, 'reset_password.html', {'form': form})


@csrf_exempt
def facebook_login_success(request):
    if request.method == 'POST':
        fb_user_id = request.POST.get('id')
        try:
            user_profile = UserProfile.objects.get(social_media_key=fb_user_id)
            user_data = User.objects.get(pk=user_profile.user_id)
            login(request, user_data)

        except:
            user_name = request.POST.get('name').split(' ')
            first_name = user_name[0]
            last_name = user_name[1]

            user_obj = User()
            user_obj.first_name = first_name
            user_obj.last_name = last_name
            user_obj.is_active = 1
            user_obj.save()

            userprofile = UserProfile()
            userprofile.user_id = user_obj.id
            userprofile.social_media_key = fb_user_id

            userprofile.save()
            login(request, user_obj)

        if request.is_ajax():
            return HttpResponse('true')
