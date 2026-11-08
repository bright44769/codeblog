from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from pathlib import Path
from .models import Post, PostMedia, Comment, Like, Bookmark

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov'}
MAX_MEDIA_SIZE = 50 * 1024 * 1024


def validate_post_media(files):
    errors = []
    for uploaded_file in files:
        extension = Path(uploaded_file.name).suffix.lower()
        if extension not in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
            errors.append(f'{uploaded_file.name}: choose a JPG, PNG, GIF, WEBP, MP4, WEBM, or MOV file.')
        if uploaded_file.size > MAX_MEDIA_SIZE:
            errors.append(f'{uploaded_file.name}: files must be 50 MB or smaller.')
    return errors


def save_post_media(post, files):
    for uploaded_file in files:
        extension = Path(uploaded_file.name).suffix.lower()
        media_type = PostMedia.IMAGE if extension in IMAGE_EXTENSIONS else PostMedia.VIDEO
        PostMedia.objects.create(post=post, file=uploaded_file, media_type=media_type)

def bloghome(request):
    posts = Post.objects.filter(is_published=True).select_related('author').prefetch_related('likes')
    category = request.GET.get('category', '').strip()
    if category: posts = posts.filter(category__iexact=category)
    paginator = Paginator(posts, 8)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/bloghome.html', {'page_obj': page_obj, 'categories': Post.objects.filter(is_published=True).exclude(category='').values_list('category', flat=True).distinct()})

def blogpost(request, slug):
    post = get_object_or_404(Post.objects.select_related('author').prefetch_related('comments__author', 'media'), slug=slug)
    if not post.is_published and post.author != request.user: return redirect('blog:home')
    if request.method == 'GET': Post.objects.filter(pk=post.pk).update(views=post.views + 1)
    liked = request.user.is_authenticated and post.likes.filter(user=request.user).exists()
    bookmarked = request.user.is_authenticated and post.bookmarks.filter(user=request.user).exists()
    if request.method == 'POST':
        if not request.user.is_authenticated: return redirect('login')
        body = request.POST.get('body', '').strip()
        if body:
            Comment.objects.create(post=post, author=request.user, body=body)
            messages.success(request, 'Your comment was added.')
        return redirect('blog:post', slug=slug)
    return render(request, 'blog/blogpost.html', {'post': post, 'liked': liked, 'bookmarked': bookmarked})

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip(); content = request.POST.get('content', '').strip()
        media_files = request.FILES.getlist('media_files')
        media_errors = validate_post_media(media_files)
        if title and content and not media_errors:
            post = Post(author=request.user, title=title, content=content, excerpt=request.POST.get('excerpt','').strip(), category=request.POST.get('category','').strip(), tags=request.POST.get('tags','').strip(), is_published=request.POST.get('action') != 'draft', cover_image=request.FILES.get('cover_image'))
            post.save()
            save_post_media(post, media_files)
            messages.success(request, 'Your post has been saved.'); return redirect('blog:post', slug=post.slug)
        if media_errors:
            for error in media_errors:
                messages.error(request, error)
        if not title or not content:
            messages.error(request, 'Please provide a title and post content.')
    return render(request, 'blog/post_form.html')

@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        media_files = request.FILES.getlist('media_files')
        media_errors = validate_post_media(media_files)
        post.title=request.POST.get('title','').strip(); post.content=request.POST.get('content','').strip(); post.excerpt=request.POST.get('excerpt','').strip(); post.category=request.POST.get('category','').strip(); post.tags=request.POST.get('tags','').strip(); post.is_published=request.POST.get('action') != 'draft'
        if request.FILES.get('cover_image'): post.cover_image=request.FILES['cover_image']
        if post.title and post.content and not media_errors:
            post.save()
            save_post_media(post, media_files)
            messages.success(request,'Post updated.'); return redirect('blog:post',slug=post.slug)
        for error in media_errors:
            messages.error(request, error)
        if not post.title or not post.content:
            messages.error(request,'Title and content are required.')
    return render(request,'blog/post_form.html',{'post':post})

@login_required
@require_POST
def delete_post(request, slug):
    post=get_object_or_404(Post,slug=slug,author=request.user); post.delete(); messages.success(request,'Post deleted.'); return redirect('blog:my_posts')

@login_required
@require_POST
def toggle_like(request, slug):
    post=get_object_or_404(Post,slug=slug,is_published=True); obj,created=Like.objects.get_or_create(post=post,user=request.user)
    if not created: obj.delete()
    return redirect(request.POST.get('next') or 'blog:post', **({'slug':slug} if not request.POST.get('next') else {}))

@login_required
@require_POST
def toggle_bookmark(request, slug):
    post=get_object_or_404(Post,slug=slug,is_published=True); obj,created=Bookmark.objects.get_or_create(post=post,user=request.user)
    if not created: obj.delete()
    return redirect(request.POST.get('next') or 'blog:post', **({'slug':slug} if not request.POST.get('next') else {}))

@login_required
def my_posts(request):
    posts=Post.objects.filter(author=request.user)
    return render(request,'blog/my_posts.html',{'posts':posts})
