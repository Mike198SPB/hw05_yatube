from http import HTTPStatus

from django.urls import reverse

GROUP_SLUG = 'slug1'
NEW_GROUP_SLUG = 'new_slug1'
GROUP_URL = reverse('posts:group_list', args=[GROUP_SLUG])
AUTHOR_USERNAME = 'author'
NOT_AUTHOR_USERNAME = 'notauthor'
POST_ID = 1
POST_TEXT = 'Test post'
NEW_POST_TEXT = 'New test post'
COMMENT_TEXT = 'Test comment'
GROUP_TITLE = 'Test group'
NEW_GROUP_TITLE = 'New test group'
GROUP_DESCRIPTION = 'Test description'
NEW_GROUP_DESCRIPTION = 'New test description'
IMAGE = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

MAIN_URL = reverse('posts:main')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR_USERNAME])
POST_URL = reverse('posts:post_detail', args=[POST_ID])
POST_EDIT_URL = reverse('posts:post_edit', args=[POST_ID])
POST_CREATE_URL = reverse('posts:post_create')
LOGIN_URL = reverse('users:login')
FOLLOW_URL = reverse('posts:profile_follow', args=[AUTHOR_USERNAME])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[AUTHOR_USERNAME])
FOLLOW_INDEX_URL = reverse('posts:follow_index')
UN_PAGE = '/unexisting_page/'

INDEX_TMPL = 'posts/index.html'
GROUP_LIST_TMPL = 'posts/group_list.html'
PROFILE_TMPL = 'posts/profile.html'
POST_DETAIL_TMPL = 'posts/post_detail.html'
POST_CREATE_TMPL = 'posts/create_post.html'
FOLLOW_TMPL = 'posts/follow.html'
TMPL_404 = 'core/404.html'

OK = HTTPStatus.OK  # 200
FOUND = HTTPStatus.FOUND  # 302
NOT_FOUND = HTTPStatus.NOT_FOUND  # 404

POSTS_COUNT_PAGINATOR_TEST = 13
