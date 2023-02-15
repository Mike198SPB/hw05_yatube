from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу для поста',
        }
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        help_texts = {
            'text': 'Введите текст комментария',
        }
        fields = ('text',)
