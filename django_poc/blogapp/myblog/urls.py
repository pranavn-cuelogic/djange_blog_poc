"""myblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, patterns, include
from django.contrib import admin
from myblog.views import *

urlpatterns = patterns(
    '',
    # url(r'^profile/(?P<user_id>[-\w]+)/$', profile_view, name='profile'),
    url(r'^profile/$', profile_view, name='profile'),
    url(r'^edit-profile/$', edit_profile, name='edit-profile'),
    url(r'^upload-pic/$', upload_pic, name='upload-pic'),
    url(r'^add-post/$', add_post, name='add-post'),
    url(r'^edit-post/$', edit_post, name='edit-post'),
    url(r'^my-blog/$', my_blog, name='my-blog'),
    url(r'^user-comment/$', user_comment, name='user-comment'),
    url(r'^delete-comment/$', delete_comment, name='delete-comment'),
    url(r'^(?P<post_slug>[-\w]+)/$', view_post, name='view-post'),
)
