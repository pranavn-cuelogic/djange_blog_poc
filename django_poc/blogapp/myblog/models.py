from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=200,)
    content = models.TextField()
    status = models.CharField(max_length=10,)
    tags = models.CharField(max_length=200,)
    rating = models.IntegerField()
    slug = models.SlugField(max_length=200,)
    created = models.DateTimeField(auto_now_add=True,)
    modified = models.DateTimeField(auto_now=True,)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment(models.Model):
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True,)
    postid = models.ForeignKey(Post, on_delete=models.CASCADE)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    phone_number = models.IntegerField(null=True,)
    address = models.TextField()
    about_me = models.TextField()
    activation_token = models.CharField(max_length=200,)
    photo = models.FileField(upload_to=None, max_length=200,)
    social_media_key = models.CharField(max_length=200,)
    created = models.DateTimeField(auto_now_add=True,)
    modified = models.DateTimeField(auto_now=True,)
