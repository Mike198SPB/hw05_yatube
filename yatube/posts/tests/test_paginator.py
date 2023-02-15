from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post
from . import const

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=const.AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION,
        )
        for i in range(const.POSTS_COUNT_PAGINATOR_TEST):
            cls.post = Post.objects.create(
                author=cls.author,
                text=const.POST_TEXT,
                group=cls.group,
            )
        cls.test_list = [const.MAIN_URL, const.GROUP_URL, const.PROFILE_URL]

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_first_page_contains_correct_records(self):
        """На первой странице пагинатора отображается корректное количество
        постов."""
        check = const.POSTS_COUNT_PAGINATOR_TEST > settings.POSTS_ON_PAGE
        posts_on_first_page = (settings.POSTS_ON_PAGE if check
                               else const.POSTS_COUNT_PAGINATOR_TEST)
        for url in self.test_list:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(len(response.context['page_obj']),
                                 posts_on_first_page)

    def test_last_page_contains_correct_records(self):
        """На послед ней странице пагинатора отображается корректное
        количество постов."""
        posts_mod = const.POSTS_COUNT_PAGINATOR_TEST % settings.POSTS_ON_PAGE
        posts_div = const.POSTS_COUNT_PAGINATOR_TEST // settings.POSTS_ON_PAGE
        last_page = posts_div if posts_mod == 0 else posts_div + 1
        last_page_url = f'?page={last_page}'
        check = posts_mod == 0 and (const.POSTS_COUNT_PAGINATOR_TEST
                                    >= settings.POSTS_ON_PAGE)
        posts_on_last_page = settings.POSTS_ON_PAGE if check else posts_mod
        for url in self.test_list:
            with self.subTest(url=url):
                response = self.author_client.get(url + last_page_url)
                self.assertEqual(len(response.context['page_obj']),
                                 posts_on_last_page)
