import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post
from . import const

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=const.AUTHOR_USERNAME)
        cls.not_author = User.objects.create_user(
            username=const.NOT_AUTHOR_USERNAME)
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
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=const.IMAGE,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=const.POST_TEXT,
            group=cls.group,
            image=cls.image,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)

        self.POST_URL = reverse('posts:post_detail', args=[self.post.id])
        self.POST_EDIT_URL = reverse('posts:post_edit', args=[self.post.id])

        self.ADD_COMMENT_URL = reverse('posts:add_comment',
                                       args=[self.post.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_url_correct_templates(self):
        """URL-адреса использует корректные шаблоны."""
        test_list = {
            const.MAIN_URL: const.INDEX_TMPL,
            const.GROUP_URL: const.GROUP_LIST_TMPL,
            const.PROFILE_URL: const.PROFILE_TMPL,
            self.POST_URL: const.POST_DETAIL_TMPL,
            self.POST_EDIT_URL: const.POST_CREATE_TMPL,
            const.POST_CREATE_URL: const.POST_CREATE_TMPL,
            const.FOLLOW_INDEX_URL: const.FOLLOW_TMPL,
        }
        for url, template in test_list.items():
            with self.subTest(address=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def check_context(self, response, flag=False):
        """Функция для проверки контекста."""
        if flag:
            post = response.context.get('post')
        else:
            post = response.context['page_obj'][0]
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.image, f'posts/{self.image}')

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.author_client.get(const.MAIN_URL)
        self.check_context(response)

    def test_follow_index_show_correct_context(self):
        """Шаблон follow сформирован с правильным контекстом."""
        self.not_author_client.get(const.FOLLOW_URL)
        response = self.not_author_client.get(const.FOLLOW_INDEX_URL)
        self.check_context(response)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.author_client.get(const.GROUP_URL)
        self.check_context(response)
        self.assertEqual(response.context.get('group'), self.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.author_client.get(const.PROFILE_URL)
        self.check_context(response)
        self.assertEqual(response.context.get('author'), self.author)
        self.assertEqual(response.context.get('posts_count'),
                         self.author.posts.count())

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(self.POST_URL)
        self.check_context(response, True)
        self.assertEqual(response.context.get('posts_count'),
                         self.author.posts.count())

    def test_edit_post_context(self):
        """Шаблон create_post для редактирования поста сформирован с правильным
        контекстом."""
        response = self.author_client.get(self.POST_EDIT_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_context(self):
        """Шаблон create_post для создания нового поста сформирован с
        правильным контекстом."""
        response = self.author_client.get(const.POST_CREATE_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_check_post_with_group_in_pages(self):
        """Созданный с группой пост появляется на страницах."""
        test_list = {
            const.MAIN_URL: Post.objects.get(group=self.post.group),
            const.GROUP_URL: Post.objects.get(group=self.post.group),
            const.PROFILE_URL: Post.objects.get(group=self.post.group),
        }
        for url, post_with_group in test_list.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                page_obj = response.context["page_obj"]
                self.assertIn(post_with_group, page_obj)

    def test_check_post_with_group_not_in_another_group(self):
        """Созданный с группой пост не попал в другую группу."""
        post = Post.objects.get(group=self.post.group)
        response = self.author_client.get(
            reverse('posts:group_list', args=[const.NEW_GROUP_SLUG]))
        page_obj = response.context["page_obj"]
        self.assertNotIn(post, page_obj)

    def test_not_author_can_comment_author_post(self):
        """Авторизованный пользователь может комментировать пост."""
        self.not_author_client.post(self.ADD_COMMENT_URL,
                                    data={'text': const.COMMENT_TEXT},
                                    )
        comment = Comment.objects.filter(post=self.post).last()
        self.assertEqual(comment.text, const.COMMENT_TEXT)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.not_author)

    def test_guest_cannot_comment_author_post(self):
        """Неавторизованный пользователь не может комментировать пост."""
        count_comments = Comment.objects.count()
        self.client.post(self.ADD_COMMENT_URL,
                         data={'text': const.COMMENT_TEXT},
                         )
        self.assertEqual(count_comments, Comment.objects.count())

    def test_main_page_cached(self):
        """Главная страница кэшируется."""
        new_post = Post.objects.create(
            author=self.author,
            text=const.NEW_POST_TEXT,
        )
        cache.clear()
        response = self.author_client.get(const.MAIN_URL)
        cached_content = response.content
        new_post.delete()
        cached_response = self.author_client.get(const.MAIN_URL)
        self.assertEqual(cached_response.content, cached_content)
        cache.clear()
        response = self.author_client.get(const.MAIN_URL)
        self.assertNotEqual(response.content, cached_content)

    def test_not_author_can_follow_author(self):
        """Авторизированный пользователь может подписаться от автора поста."""
        self.not_author_client.get(const.FOLLOW_URL)
        follower = Follow.objects.get(user=self.not_author)
        self.assertEqual(self.author, follower.author)

    def test_follower_can_unfollow_from_author(self):
        """Авторизованный подписчик может отписаться от автора поста."""
        self.not_author_client.get(const.FOLLOW_URL)
        self.not_author_client.get(const.UNFOLLOW_URL)
        unfollowing = Follow.objects.filter(user=self.not_author,
                                            author=self.author)
        self.assertFalse(unfollowing)

    def test_post_is_shown_for_follower(self):
        """Пост автора появляется в ленте тех, кто на него подписан."""
        self.not_author_client.get(const.FOLLOW_URL)
        response = self.not_author_client.get(const.FOLLOW_INDEX_URL)
        self.assertIn(self.post, response.context['page_obj'])

    def test_post_not_shown_for_unfollower(self):
        """Пост автора не появляется в ленте тех, кто на него не подписан"""
        response = self.not_author_client.get(const.FOLLOW_INDEX_URL)
        self.assertNotIn(self.post, response.context['page_obj'])
