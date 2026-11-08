from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Post, PostMedia, Comment, Like, Bookmark

class BloggingFlowTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username='writer',password='Test-pass-12345')
        self.post=Post.objects.create(author=self.user,title='A test story',content='This is a useful test story.')
    def test_post_slug_is_generated(self):
        self.assertEqual(self.post.slug,'a-test-story')
    def test_post_is_visible(self):
        response=self.client.get(reverse('blog:post',kwargs={'slug':self.post.slug}))
        self.assertEqual(response.status_code,200)
    def test_authenticated_user_can_comment(self):
        self.client.login(username='writer',password='Test-pass-12345')
        response=self.client.post(reverse('blog:post',kwargs={'slug':self.post.slug}),{'body':'Helpful post'})
        self.assertEqual(response.status_code,302)
        self.assertEqual(Comment.objects.count(),1)
    def test_like_is_unique_per_user(self):
        Like.objects.create(post=self.post,user=self.user)
        self.assertEqual(self.post.likes.count(),1)
    def test_bookmark_is_unique_per_user(self):
        Bookmark.objects.create(post=self.post,user=self.user)
        self.assertEqual(self.post.bookmarks.count(),1)

    def test_story_can_include_uploaded_images_and_videos(self):
        self.client.login(username='writer',password='Test-pass-12345')
        response=self.client.post(reverse('blog:create'), {
            'title': 'A story with media',
            'content': 'This story includes an image and a video.',
            'action': 'publish',
            'media_files': [
                SimpleUploadedFile('photo.png', b'image-data', content_type='image/png'),
                SimpleUploadedFile('clip.mp4', b'video-data', content_type='video/mp4'),
            ],
        })

        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(slug='a-story-with-media')
        self.assertEqual(
            set(post.media.values_list('media_type', flat=True)),
            {PostMedia.IMAGE, PostMedia.VIDEO},
        )

        response=self.client.get(reverse('blog:post', kwargs={'slug': post.slug}))
        self.assertContains(response, '<video controls', html=False)
        self.assertContains(response, 'post_media/photo.png', html=False)

    def test_story_media_rejects_unsupported_file_types(self):
        self.client.login(username='writer',password='Test-pass-12345')
        response=self.client.post(reverse('blog:create'), {
            'title': 'Story with invalid media',
            'content': 'The upload should be rejected.',
            'media_files': SimpleUploadedFile('script.exe', b'not-allowed'),
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(title='Story with invalid media').exists())
        self.assertContains(response, 'choose a JPG, PNG, GIF, WEBP, MP4, WEBM, or MOV file')

    def test_theme_toggle_is_available(self):
        response=self.client.get(reverse('home'))

        self.assertContains(response, 'Switch to dark mode')
        self.assertContains(response, 'js/theme.js')
