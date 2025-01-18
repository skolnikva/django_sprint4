from django import forms
from .models import Post, Comment
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import datetime


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'location', 'category',
                  'is_published', 'image']
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }

    def clean_pub_date(self):
        pub_date = self.cleaned_data.get('pub_date')

        if not pub_date:
            raise ValidationError("Введите корректную дату публикации.")

        if not isinstance(pub_date, datetime.date):
            raise ValidationError("Используйте корректный формат YYYY-MM-DD.")

        return pub_date


class UserEditForm(UserChangeForm):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3,
                                          'placeholder': 'Ваш комментарий..'}),
        }
