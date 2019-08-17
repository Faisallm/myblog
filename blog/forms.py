from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=100)
    to = forms.EmailField(max_length=100)
    comments = forms.CharField(widget=forms.Textarea,
                                required=False)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')

class SearchForm(forms.Form):
    query = forms.CharField()