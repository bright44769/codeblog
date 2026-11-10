from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from blog.models import Post
from .forms import RegistrationForm, SiteReviewForm
from .models import Contact, Profile

def home(request):
    posts=Post.objects.filter(is_published=True).select_related('author')[:6]
    return render(request,'home/home.html',{'posts':posts})
def about(request): return render(request,'home/about.html')
def contact(request):
    if request.method=='POST':
        name=request.POST.get('name','').strip(); email=request.POST.get('email','').strip(); content=request.POST.get('message','').strip()
        if name and email and content:
            Contact.objects.create(name=name,email=email,phone=request.POST.get('phone','').strip(),content=content); messages.success(request,'Thanks! Your message has been sent.')
            return redirect('contact')
        messages.error(request,'Please complete the required fields.')
    return render(request,'home/contact.html')

@login_required
def review(request):
    form = SiteReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        site_review = form.save(commit=False)
        site_review.user = request.user
        site_review.save()
        messages.success(request, 'Thanks for sharing your feedback.')
        return redirect('review')
    return render(request, 'home/review.html', {'form': form})

def search(request):
    query=request.GET.get('query','').strip()
    posts=Post.objects.filter(is_published=True).filter(Q(title__icontains=query)|Q(content__icontains=query)|Q(tags__icontains=query)|Q(category__icontains=query)) if query else Post.objects.none()
    return render(request,'home/search.html',{'allPosts':posts,'query':query})
def register(request):
    form=RegistrationForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=form.save()
        login(request,user,backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')
    return render(request,'registration/register.html',{'form':form})

@login_required
def profile(request, username=None):
    if username is None and not request.user.is_authenticated: return redirect('login')
    target=get_object_or_404(User,username=username) if username else request.user
    profile_obj, _=Profile.objects.get_or_create(user=target)
    if request.user==target and request.method=='POST':
        profile_obj.bio=request.POST.get('bio','')[:500]; profile_obj.website=request.POST.get('website',''); profile_obj.location=request.POST.get('location','')
        if request.FILES.get('avatar'): profile_obj.avatar=request.FILES['avatar']
        profile_obj.save(); messages.success(request,'Profile updated.'); return redirect('profile')
    posts=Post.objects.filter(author=target,is_published=True)
    return render(request,'home/profile.html',{'profile_user':target,'profile_obj':profile_obj,'posts':posts,'is_owner':request.user==target})
