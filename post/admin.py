from django.contrib import admin
from .models import Post, PostLike, PostComment, CommentLike


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'caption', 'created_time']
    search_fields = ['author__username', 'caption']


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'created_time']
    search_fields = ['author__username', 'comment']


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'created_time']
    search_fields = ['author__username']


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'comment', 'created_time']
    search_fields = ['author__username']


