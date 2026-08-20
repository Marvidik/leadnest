# accounts/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import FilteredSelectMultiple
from ckeditor.widgets import CKEditorWidget


User = get_user_model()

class BroadcastEmailForm(forms.Form):
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=CKEditorWidget())
    send_to_all = forms.BooleanField(required=False, label="Send to ALL users")
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("Users", is_stacked=False),
    )