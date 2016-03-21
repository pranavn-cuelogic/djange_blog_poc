from django.contrib import admin

# Register your models here.
from .models import UserProfile, Post, Comment

class PostAdmin(admin.ModelAdmin):
    fields = ['title', 'content', 'slug', 'tags', 'status', 'userid']
    list_filter = ['created']
    search_fields = ['title']

admin.site.register(Post, PostAdmin)
admin.site.register(UserProfile)
admin.site.register(Comment)
