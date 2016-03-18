from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, loader
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from blogapp.forms import UserProfileForm, UploadUserPicForm, PostForm
import random, sha, re, os
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from myblog.models import UserProfile, Post, Comment
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
    return get_tags

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


@user_passes_test(user_only, login_url='login')
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


@user_passes_test(user_only, login_url='login')
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


@user_passes_test(user_only, login_url='login')
def edit_post(request):
    post_id = request.GET.get('id', None)

    if post_id is not None:
        post = get_object_or_404(Post, id=post_id)
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
                'status': request.POST.get('status', None),
                'slug': slugify(request.POST.get('title', None))
            }

            Post.objects.filter(id=post_id).update(**post_dict)

            success_message = "Post updated successfully"

            messages.add_message(request, messages.INFO, success_message)
            return HttpResponseRedirect(reverse('home'))

    else:
        postform = PostForm(initial=postdata)

    return render(request, 'myblog/edit_post.html', {'form': postform})


def view_post(request, **kwargs):
    post_slug = kwargs['post_slug']

    post = get_object_or_404(Post, slug=post_slug)

    blog_data = {}
    if post:

        blog_data['post_info'] = post
        blog_data['post_info'].tags = get_tags(post.content)
        blog_data['comments_count'] = Comment.objects.filter(postid_id=post.id).count()
        blog_data['user_obj'] = User.objects.get(id=post.userid.id)
        blog_data['user_profile'] = UserProfile.objects.get(user_id=post.userid.id)

        comments = Comment.objects.filter(postid_id=post.id)

        user_comments_list = []
        for each in comments:
            user_comment_data = {}

            user_comment_data['comment'] = each
            user_comment_data['user_obj'] = User.objects.get(id=each.userid.id)
            user_comment_data['user_profile'] = UserProfile.objects.get(user_id=each.userid.id)

            if not user_comment_data['user_profile'].photo:
                user_comment_data['user_profile'] = 'default.png'

            user_comments_list.append(user_comment_data)

    if not blog_data['user_profile'].photo:
        blog_data['user_profile'].photo = 'default.png'
    blog_info = {'blog_data': blog_data, 'comments': user_comments_list}
    return render(request, 'myblog/view_post.html', blog_info)


@user_passes_test(user_only, login_url='login')
def my_blog(request):
    blog_data = Post.objects.filter(userid_id=request.user.id)
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    blog_info = {'blog_data': blog_data, 'user_profile': user_profile, 'user_data': request.user}
    return render(request, 'myblog/my_blog.html', blog_info)


@csrf_exempt
def user_comment(request):
    if request.method == 'POST':
        comment = request.POST.get('comment', None)
        post_id = request.POST.get('post_id', None)
        slug = request.POST.get('slug', None)

        comment_data = Comment()

        comment_data.comment = comment
        comment_data.postid_id = post_id
        comment_data.userid_id = request.user.id

        comment_data.save()
        comment_obj = {}
        comment_obj['comment'] = comment_data
        comment_obj['user_obj'] = User.objects.get(id=comment_data.userid_id)
        comment_obj['user_profile'] = UserProfile.objects.get(user_id=comment_data.userid_id)
        comment_obj['current_user'] = request.user

        if not comment_obj['user_profile'].photo:
            comment_obj['user_profile'].photo = 'default.png'

        if not request.user.id == comment_obj['user_obj'].id:

            post_data = Post.objects.get(id=post_id)
            user_data = User.objects.get(id=post_data.userid_id)

            current_domain = settings.SITE_URL
            subject = comment_obj['user_obj'].first_name, "commented on your post!"
            message_template = loader.get_template('email_content/comment_notification.txt')
            message_context = Context({
                'user_name': user_data.first_name + ' ' + user_data.last_name,
                'guest_name': comment_obj['user_obj'].first_name + ' ' + comment_obj['user_obj'].last_name,
                'post_url': 'http://%s/myblog/%s' % (current_domain, slug),
                'comment': comment_data.comment,
            })
            message = message_template.render(message_context)
            send_mail(subject, message, 'no-reply@gmail.com', [user_data.email])

        if request.is_ajax():
            html = render_to_string('myblog/comment_data.html', {'comment_obj': comment_obj})
            return HttpResponse(html)


@csrf_exempt
def delete_comment(request):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id', None)
        print comment_id
        Comment.objects.get(pk=comment_id).delete()

        if request.is_ajax():
            html = '<p>True</p>'
            return HttpResponse(html)
