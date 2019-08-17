from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager

class PublishedManager(models.Manager):
    """retrieve published posts only."""
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset()\
                                            .filter(status='published')

class ActiveManager(models.Manager):
    def get_queryset(self):
        super(ActiveManager, self).get_queryset() \
                                    .filter(active=True)

class Post(models.Model):
    """Each attribute represents a database field."""

    STATUS = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    # each slug should have a unique publish time independent of their titles.
    author = models.ForeignKey(User, related_name='blogs_created', on_delete=models.CASCADE)
    # user.blogs_created.all()
    body = models.TextField()  # the body of the post
    publish = models.DateTimeField(default=timezone.now)  # time when objects was created
    # similar to created
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)  # last time post was updated

    status = models.CharField(choices=STATUS,
                            max_length=10,
                            default='draft')
    tags = TaggableManager()  # tags

    objects = models.Manager()  # default manager
    published = PublishedManager()  # custom manager

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                    args=[
                        self.publish.year,
                        self.publish.strftime('%m'),
                        self.publish.strftime('%d'),
                        self.slug
                    ])

    # most recent posts at the top
    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def __save__(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            return super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    objects = models.Manager()  # default manager
    actives = ActiveManager()  # custom made manager
    # comments.objects.all() or comments.active.all()
    class Meta:
        ordering = ('created',)

    def __str__(self):
        return "comment on {} by {}".format(self.post, self.name)
