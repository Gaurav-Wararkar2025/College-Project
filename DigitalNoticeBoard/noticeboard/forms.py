from django import forms
from .models import Notice

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'category', 'image', 'attachment']
        fields = '__all__'