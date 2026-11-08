import logging
from smtplib import SMTPException
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string


logger = logging.getLogger(__name__)


def send_mfa_code(request, user, *, resend=False):
    if not user.email:
        messages.error(request, 'Your account has no email address for verification.')
        return False

    code = get_random_string(length=6, allowed_chars='0123456789')
    request.session['mfa_code'] = code
    request.session['mfa_code_expires_at'] = (
        timezone.now() + timedelta(minutes=10)
    ).isoformat()
    request.session['mfa_pending'] = True
    request.session['mfa_verified'] = False

    subject = (
        'Your new CodeBlog verification code'
        if resend else 'Your CodeBlog verification code'
    )
    message = (
        f'Your CodeBlog verification code is {code}. '
        'Use it to finish signing in before access is granted. '
        'This code expires in 10 minutes.'
    )

    try:
        sent = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except (OSError, SMTPException):
        logger.exception('Could not send MFA email to user id %s', user.pk)
        request.session.pop('mfa_code', None)
        request.session.pop('mfa_code_expires_at', None)
        messages.error(
            request,
            'We could not send your verification email. Check the email settings '
            'and server terminal, then request a new code.',
        )
        return False

    if not sent:
        logger.error('Email backend did not send MFA email to user id %s', user.pk)
        request.session.pop('mfa_code', None)
        request.session.pop('mfa_code_expires_at', None)
        messages.error(request, 'The email service did not send your verification code.')
        return False

    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        messages.warning(
            request,
            'Email is in development console mode. The code was printed in the '
            'Django server terminal, not sent to your inbox.',
        )
    else:
        messages.success(
            request,
            f'A verification code was emailed to {user.email}. Check your spam folder if needed.',
        )
    return True
