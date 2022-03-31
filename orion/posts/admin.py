from django.contrib import admin
from posts.models import Post
from django.db import models
from tinymce.widgets import TinyMCE


class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'status', 'user']
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }


admin.site.register(Post, PostAdmin)
