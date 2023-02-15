from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from . import const

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=const.AUTHOR_USERNAME)
        cls.not_author = User.objects.create_user(
            username=const.NOT_AUTHOR_USERNAME)
        cls.post = Post.objects.create(
            author=cls.author,
            text=const.POST_TEXT,
        )
        cls.group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)

        self.user_list = [
            self.client,
            self.author_client,
            self.not_author_client
        ]

        self.POST_URL = reverse('posts:post_detail', args=[self.post.id])
        self.POST_EDIT_URL = reverse('posts:post_edit', args=[self.post.id])

    def test_url_available_for_different_types_users(self):
        """URL-адреса доступны различным пользователям."""
        test_list = [
            [const.MAIN_URL, self.user_list, (const.OK,) * 3],
            [const.GROUP_URL, self.user_list, (const.OK,) * 3],
            [const.PROFILE_URL, self.user_list, (const.OK,) * 3],
            [self.POST_URL, self.user_list, (const.OK,) * 3],
            [self.POST_EDIT_URL, self.user_list,
             (const.FOUND, const.OK, const.FOUND)],
            [const.POST_CREATE_URL, self.user_list,
             (const.FOUND, const.OK, const.OK)],
            [const.UN_PAGE, self.user_list, (const.NOT_FOUND,) * 3],
            [const.FOLLOW_INDEX_URL, self.user_list,
             (const.FOUND, const.OK, const.OK)],
        ]

        for url, user_list, status_code_list in test_list:
            for user, status_code in zip(user_list, status_code_list):
                with self.subTest(address=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status_code)

    def test_url_correct_templates(self):
        """URL-адреса использует корректные шаблоны."""
        test_list = [
            [const.MAIN_URL, self.user_list, (const.INDEX_TMPL,) * 3],
            [const.GROUP_URL, self.user_list, (const.GROUP_LIST_TMPL,) * 3],
            [const.PROFILE_URL, self.user_list, (const.PROFILE_TMPL,) * 3],
            [self.POST_URL, self.user_list, (const.POST_DETAIL_TMPL,) * 3],
            [self.POST_EDIT_URL, (self.author_client,),
             (const.POST_CREATE_TMPL,)],
            [const.POST_CREATE_URL,
             (self.author_client, self.not_author_client),
             (const.POST_CREATE_TMPL, const.POST_CREATE_TMPL)],
            [const.UN_PAGE, self.user_list, (const.TMPL_404,) * 3],
            [const.FOLLOW_INDEX_URL,
             (self.author_client, self.not_author_client),
             (const.FOLLOW_TMPL, const.FOLLOW_TMPL)],
        ]
        for url, user_list, template_list in test_list:
            for user, template in zip(user_list, template_list):
                with self.subTest(address=url):
                    response = user.get(url)
                    self.assertTemplateUsed(response, template)

    def test_create_url_for_unauthorized_redirect_login(self):
        """Со страницы /create/ происходит редирект
        неавторизованных пользователей."""
        response = self.client.get(const.POST_CREATE_URL, follow=True)
        self.assertRedirects(response,
                             const.LOGIN_URL + '?next='
                             + const.POST_CREATE_URL)

    def test_post_edit_url_for_notauthor_redirect_post_detail(self):
        """Со страницы /posts/<post_id>/edit/ происходит редирект
        авторизованного не автора поста."""
        response = self.not_author_client.get(self.POST_EDIT_URL, follow=True)
        self.assertRedirects(response, self.POST_URL)

    def test_post_edit_url_for_unauthorized_redirect_login(self):
        """Со страницы /posts/<post_id>/edit/ происходит редирект
        неавторизованного пользователя."""
        response = self.client.get(self.POST_EDIT_URL, follow=True)
        self.assertRedirects(response,
                             const.LOGIN_URL + '?next=' + self.POST_EDIT_URL)

    def test_follow_url_for_unauthorized_redirect_login(self):
        """Со страницы /follow/ происходит редирект
         неавторизованных пользователей."""
        response = self.client.get(const.FOLLOW_INDEX_URL, follow=True)
        self.assertRedirects(response,
                             const.LOGIN_URL + '?next='
                             + const.FOLLOW_INDEX_URL)
