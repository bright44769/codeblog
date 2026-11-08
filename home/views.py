from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from blog.models import Post
from .forms import RegistrationForm
from .mfa import send_mfa_code as issue_mfa_code
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
def search(request):
    query=request.GET.get('query','').strip()
    posts=Post.objects.filter(is_published=True).filter(Q(title__icontains=query)|Q(content__icontains=query)|Q(tags__icontains=query)|Q(category__icontains=query)) if query else Post.objects.none()
    return render(request,'home/search.html',{'allPosts':posts,'query':query})
def register(request):
    form=RegistrationForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=form.save()
        login(request,user,backend='django.contrib.auth.backends.ModelBackend')
        return redirect('mfa_verify')
    return render(request,'registration/register.html',{'form':form})


def mfa_verify(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.session.get('mfa_verified'):
        return redirect('home')

    if request.method == 'POST':
        submitted_code = request.POST.get('code', '').strip()
        expected_code = request.session.get('mfa_code')
        expires_at = request.session.get('mfa_code_expires_at')

        if expected_code and expires_at:
            try:
                expires_at_dt = datetime.fromisoformat(expires_at)
            except ValueError:
                expires_at_dt = None

            if expires_at_dt and timezone.now() < expires_at_dt and submitted_code == expected_code:
                request.session['mfa_verified'] = True
                request.session['mfa_pending'] = False
                request.session.pop('mfa_code', None)
                request.session.pop('mfa_code_expires_at', None)
                messages.success(request, 'Email verification passed. You are now signed in.')
                return redirect('home')

        messages.error(request, 'Invalid or expired verification code. Please try again.')

    return render(request, 'registration/mfa_verify.html', {'user_email': request.user.email})


def resend_mfa_code(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.email:
        messages.error(request, 'Add an email address to your account before enabling MFA.')
        return redirect('profile')

    issue_mfa_code(request, request.user, resend=True)
    return redirect('mfa_verify')


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
