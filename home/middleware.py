from django.shortcuts import redirect
from django.urls import reverse


class RequireEmailMFA(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.session.get('mfa_verified'):
            allowed_paths = {
                reverse('logout'),
                reverse('login'),
                reverse('mfa_verify'),
                reverse('mfa_resend'),
                reverse('password_change'),
                '/accounts/google/login/',
                '/accounts/google/login/callback/',
                '/accounts/google/signup/',
                '/admin/logout/',
                '/admin/login/',
                '/static/',
                '/media/',
            }
            if not any(request.path == path or request.path.startswith(path) for path in allowed_paths):
                if request.path.startswith('/admin/'):
                    return redirect('mfa_verify')
                return redirect('mfa_verify')
        return self.get_response(request)
