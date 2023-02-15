import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post
from . import const

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=const.AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION,
        )
        cls.new_group = Group.objects.create(
            title=const.NEW_GROUP_TITLE,
            slug=const.NEW_GROUP_SLUG,
            description=const.NEW_GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=const.POST_TEXT,
            group=cls.group,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """При отправке валидной формы (с картинкой) со страницы создания поста
        создаётся новая запись в базе данных и происходит редирект
        на страницу профиля автора"""
        posts_count = Post.objects.count()
        image = SimpleUploadedFile(
            name='small.gif',
            content=const.IMAGE,
            content_type='image/gif'
        )
        form_data = {
            'text': const.POST_TEXT,
            'group': self.group.id,
            'image': image,
        }
        response = self.author_client.post(
            const.POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        post = Post.objects.filter(
            text=const.POST_TEXT,
            group=self.group.id,
            author=self.author,
        )
        self.assertRedirects(response, const.PROFILE_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(post.exists())
        self.assertEqual(post[0].image, f'posts/{image}')

    def test_post_edit(self):
        """При отправке валидной формы (с картинкой) со страницы редактирования
        поста происходит изменение поста с post_id в базе данных."""
        POST_URL = reverse('posts:post_detail', args=[self.post.id])
        POST_EDIT_URL = reverse('posts:post_edit', args=[self.post.id])
        posts_count = Post.objects.count()
        image = SimpleUploadedFile(
            name='new_small.gif',
            content=const.IMAGE,
            content_type='image/gif'
        )
        form_data = {
            'text': const.NEW_POST_TEXT,
            'group': self.group.id,
            'image': image,
        }
        response = self.author_client.post(
            POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        post = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, POST_URL)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image, f'posts/{image}')
