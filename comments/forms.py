from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Comment,Page

class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with email field"""
    email = forms.EmailField(required=True)
        
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CommentForm(forms.ModelForm):
    parent_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your thoughts...',
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        parent_id = kwargs.pop('parent_id', None)
        super().__init__(*args, **kwargs)
        if parent_id:
            self.fields['parent_id'].initial = str(parent_id)
            self.fields['content'].widget.attrs['placeholder'] = 'Write your reply...'
    
    def clean_parent_id(self):
        parent_id = self.cleaned_data.get('parent_id')
        if parent_id:
            try:
                # Convert to int and get the Comment object
                parent_comment = Comment.objects.get(id=int(parent_id))
                return parent_comment  # Return the Comment object, not the ID
            except (ValueError, Comment.DoesNotExist):
                raise forms.ValidationError("Parent comment not found.")
        return None
    
class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter discussion title...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Write your discussion content...'
            }),
        }