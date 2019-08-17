from django.contrib import admin
from .models import Post, Comment

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'slug', 'publish', 'status')
    list_filter = ('created' , 'updated', 'status')
    date_hierarchy = 'publish'
    prepopulated_fields = {'slug':('title',)}
    raw_id_fields = ('author',)
    search_fields = ('title', 'body')

class CommentAdmin(admin.ModelAdmin):
    list_diplay = ('name', 'email', 'post', 'created' ,'active')
    list_filter = ('created', 'updated', 'active')
    date_hierarchy = 'created'
    search_fields = ('name', 'body', 'post')

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)