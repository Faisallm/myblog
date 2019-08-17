from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

def post_list(request, tag_slug=None):
    tag = None
    objects_list = Post.objects.all()

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        objects_list = objects_list.filter(tags__in=[tag])

    paginator = Paginator(objects_list, 3)  # 3 posts per page
    page_number = request.GET.get('page')

    try:
        posts = paginator.page(page_number)  # obtain posts
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request,
                    'blog/post/list.html',
                    {'posts':posts,
                    'page':page_number,
                    'tag':tag})


def post_detail(request, year, month, day, slug):
    post = get_object_or_404(Post, slug=slug,
                                    status='published',
                                    publish__year=year,
                                    publish__month=month,
                                    publish__day=day)
    new_comment = None

    comments = post.comments.filter(active=True)  # retrieve comments of the post
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)  # prepopulate form with the user's data.
        if comment_form.is_valid:
            new_comment = comment_form.save(commit=False)  # created form instance but don't save  to database yet
            new_comment.post = post
            new_comment.save()  # save to database

    else:
        comment_form = CommentForm()

    all_post_tags = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=all_post_tags)\
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
        .order_by('-same_tags', '-publish')[0:4]


    return render(request,
                'blog/post/detail.html',
                {'post':post,
                'comments':comments,
                'comment_form':comment_form,
                'new_comment':new_comment,
                'similar_posts':similar_posts})

def post_share(request, id):
    post = get_object_or_404(Post, id=id)
    sent=False
    cd=None

    if request.method == 'POST':
        form = EmailPostForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends your reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.\
                format(post.title, post_url, cd['name'], cd['comments'])
            #send the form
            send_mail(subject, message, cd['email'], [cd['to']], fail_silently=False)
            sent=True

    else:
        form = EmailPostForm()

    return render(request,
        'blog/post/share.html',
        {'post':post,
        'form':form,
        'sent':sent,
        'cd':cd})


def post_search(request):
    form = SearchForm()  # empty search form
    results = []
    query = None

    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']  # obtain search term
            search_query = SearchQuery(query)   # stemming
            search_vector = SearchVector('title', 'body')  # where to search
            results = Post.objects.annotate(search=search_vector,
            rank=SearchRank(search_vector, search_query)).filter(search=search_query)\
                .order_by('-rank')
    
    return render(request,
            'blog/post/search.html',
            {'results':results,
            'form':form,
            'query':query})
    