from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from blog.models import Post
from .models import SiteReview


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEBUG=True,
    PUBLIC_SITE_URL='',
)
class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='Original-pass-12345',
        )

    def test_login_page_links_to_password_reset(self):
        response = self.client.get(reverse('login'))

        self.assertContains(response, reverse('password_reset'))
        self.assertContains(response, 'autocomplete="off"')
        self.assertContains(response, 'autocomplete="new-password"')
        self.assertContains(response, 'name="username" autocomplete="off" value="" readonly')

    def test_password_reset_emails_link_to_account_email(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': self.user.email},
        )

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn('/accounts/reset/', mail.outbox[0].body)
        self.assertIsNotNone(mail.outbox[0].alternatives)
        self.assertIn('href="http://testserver/accounts/reset/', mail.outbox[0].alternatives[0][0])

    @override_settings(PUBLIC_SITE_URL='https://codeblog.example')
    def test_password_reset_uses_configured_public_site_url(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': self.user.email},
        )

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertIn(
            'https://codeblog.example/accounts/reset/',
            mail.outbox[0].body,
        )

    def test_unknown_email_does_not_disclose_account_existence(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': 'unknown@example.com'},
        )

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(mail.outbox, [])

    def test_google_only_user_with_verified_email_receives_reset_link(self):
        google_user = User.objects.create_user(
            username='google-reader',
            email='google-reader@example.com',
        )
        google_user.set_unusable_password()
        google_user.save(update_fields=['password'])
        SocialAccount.objects.create(
            user=google_user,
            provider='google',
            uid='google-reader-uid',
            extra_data={'email': google_user.email, 'email_verified': True},
        )
        EmailAddress.objects.create(
            user=google_user,
            email=google_user.email,
            verified=True,
            primary=True,
        )

        response = self.client.post(
            reverse('password_reset'),
            {'email': google_user.email},
        )

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [google_user.email])
        self.assertIn('/accounts/reset/', mail.outbox[0].body)

    def test_unverified_google_only_user_does_not_receive_reset_link(self):
        google_user = User.objects.create_user(
            username='unverified-google-reader',
            email='unverified-google-reader@example.com',
        )
        google_user.set_unusable_password()
        google_user.save(update_fields=['password'])
        SocialAccount.objects.create(
            user=google_user,
            provider='google',
            uid='unverified-google-reader-uid',
            extra_data={'email': google_user.email, 'email_verified': False},
        )
        EmailAddress.objects.create(
            user=google_user,
            email=google_user.email,
            verified=False,
            primary=True,
        )

        response = self.client.post(
            reverse('password_reset'),
            {'email': google_user.email},
        )

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(mail.outbox, [])


class LoginFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='login-reader',
            email='login-reader@example.com',
            password='Original-pass-12345',
        )

    def test_login_completes_without_sending_verification_email(self):
        response = self.client.post(reverse('login'), {
            'username': 'login-reader',
            'password': 'Original-pass-12345',
        })

        self.assertRedirects(response, reverse('home'))
        self.assertEqual(mail.outbox, [])
        self.assertNotIn('mfa_code', self.client.session)


class SiteReviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='review-reader',
            email='review-reader@example.com',
            password='Original-pass-12345',
        )

    def test_signed_in_user_can_view_feedback_form(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('review'))

        self.assertContains(response, 'How has your experience with CodeBlog been?')
        self.assertContains(response, 'What were you expecting from the site?')

    def test_signed_in_user_can_submit_site_feedback(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('review'), {
            'experience': 'Publishing stories is straightforward.',
            'expectations': 'I hoped to find a welcoming writing community.',
        })

        self.assertRedirects(response, reverse('review'))
        saved_review = SiteReview.objects.get()
        self.assertEqual(saved_review.user, self.user)
        self.assertEqual(saved_review.experience, 'Publishing stories is straightforward.')
        self.assertEqual(saved_review.expectations, 'I hoped to find a welcoming writing community.')

    def test_anonymous_user_is_sent_to_login(self):
        response = self.client.get(reverse('review'))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('review')}")


class SearchInjectionTests(TestCase):
    def test_search_treats_sql_syntax_as_search_text(self):
        user = User.objects.create_user(username='search-writer')
        Post.objects.create(
            author=user,
            title='Private story title',
            content='Private story content',
        )

        response = self.client.get(
            reverse('search'),
            {'query': "%' OR 1=1 --"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No matching stories found.')
        self.assertNotContains(response, 'Private story title')
