from django import forms
from django.db.models.functions import Now

from .models import Post, Comment
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        empty_value_display = 'Не задано'
        fields = ('title',
                  'text',
                  'image',
                  'pub_date',
                  'location',
                  'category')
        widgets = {'pub_date': forms.DateTimeInput(
            attrs={'type': 'datetime-local'})}
