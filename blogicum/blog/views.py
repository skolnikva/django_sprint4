from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from .models import Post, Category, Comment
from django.contrib.auth import get_user_model
from .forms import (
    PostForm, UserEditForm, CommentForm,
)
from .models import Post
from django.db.models import Count
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound

User = get_user_model()


def index(request):
    post_list = Post.objects.filter(
        pub_date__lte=now(),
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date').annotate(comment_count=Count('comments'))
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    instance = get_object_or_404(
        Post,
        pk=id,
    )
    pub = instance.is_published
    cat_pub = instance.category.is_published
    time = instance.pub_date > now()
    if (not pub or not cat_pub or time) and instance.author != request.user:
        return HttpResponseNotFound()

    comments = instance.comments.all()
    form = CommentForm()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = instance
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', id=id)
    context = {'post': instance, 'form': form, 'comments': comments}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    post_list = Post.objects.filter(
        pub_date__lte=now(),
        is_published=True,
        category=get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
    ).order_by('-pub_date').annotate(comment_count=Count('comments'))
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    category = get_object_or_404(Category, slug=category_slug)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, 'blog/category.html', context)


def profile(request, username):
    instance = get_object_or_404(
        User,
        username=username,
    )
    if instance:
        post_list = Post.objects.filter(
            author=instance,
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))
        paginator = Paginator(post_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None
    context = {'profile': instance, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
        return render(request, 'blog/create.html', {'form': form})
    else:
        form = PostForm(instance=request.user)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, id):
    post = get_object_or_404(
        Post,
        pk=id
    )
    if post.author != request.user:
        return redirect('blog:post_detail', id=id)
    else:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('blog:post_detail', id=id)
        else:
            form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, id):
    post = get_object_or_404(
        Post,
        pk=id
    )
    if post.author == request.user:
        if request.method == 'POST':
            post.delete()
            return redirect('blog:profile', username=request.user.username)
    else:
        return redirect('blog:post_detail', id=id)
    return render(request, 'blog/create.html')


@login_required
def add_comment(request, id):
    post = get_object_or_404(Post, pk=id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', id=id)
    else:
        form = CommentForm()
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': form,
    })


@login_required
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', id=post_id)
    else:
        if request.method == 'POST':
            form = CommentForm(request.POST, instance=comment)

            if form.is_valid():
                form.save()
                return redirect('blog:post_detail', id=post_id)
        else:
            form = CommentForm(instance=comment)
        context = {
            'form': form,
            'post': post,
            'comment': comment,
        }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, id, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author == request.user:
        if request.method == 'POST':
            comment.delete()
            return redirect('blog:post_detail', id=id)
        else:
            return render(request, 'blog/comment.html', {'comment': comment})
    else:
        return redirect('blog:post_detail', id=id)
