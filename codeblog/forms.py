from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ImproperlyConfigured
from urllib.parse import urlsplit


class CodeBlogPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        yield from super().get_users(email)

        User = get_user_model()
        email_field = User.get_email_field_name()
        social_users = User._default_manager.filter(
            **{
                f'{email_field}__iexact': email,
                'is_active': True,
                'password__startswith': '!',
                'socialaccount__provider': 'google',
            }
        ).distinct()

        from allauth.account.models import EmailAddress

        verified_user_ids = set(
            EmailAddress.objects.filter(
                user__in=social_users,
                email__iexact=email,
                verified=True,
            ).values_list('user_id', flat=True)
        )

        for user in social_users:
            if user.pk in verified_user_ids:
                yield user

    def save(
        self,
        domain_override=None,
        subject_template_name='registration/password_reset_subject.txt',
        email_template_name='registration/password_reset_email.txt',
        use_https=False,
        token_generator=None,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        if settings.PUBLIC_SITE_URL:
            site_url = urlsplit(settings.PUBLIC_SITE_URL)
            if site_url.scheme not in {'http', 'https'} or not site_url.netloc:
                raise ImproperlyConfigured(
                    'PUBLIC_SITE_URL must be an absolute http:// or https:// URL.'
                )
            domain_override = site_url.netloc
            use_https = site_url.scheme == 'https'
        elif settings.DEBUG and request is not None:
            domain_override = request.get_host()

        kwargs = {
            'domain_override': domain_override,
            'subject_template_name': subject_template_name,
            'email_template_name': email_template_name,
            'use_https': use_https,
            'from_email': from_email,
            'request': request,
            'html_email_template_name': html_email_template_name,
            'extra_email_context': extra_email_context,
        }
        if token_generator is not None:
            kwargs['token_generator'] = token_generator

        return super().save(**kwargs)
