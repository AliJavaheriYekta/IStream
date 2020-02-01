from urllib import request

from django import forms
from django.utils.text import slugify
from django.core.files.base import ContentFile
from .models import Comment, Stream
from django.utils.translation import ugettext_lazy as _


class StreamCreateForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = ('user_name', 'game')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class SearchForm(forms.Form):
    name = forms.CharField()

