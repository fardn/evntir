from django import forms
from django.contrib.auth.forms import UserChangeForm

from eventinfo.models import Profile


class EventSearchForm(forms.Form):
    q = forms.CharField(label='دنبال چی می‌گردی؟', required=False)
    # gi_profile = forms.BooleanField(required=False)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['mobile', 'gender', 'bday', 'user_image']


class UserForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = ['first_name', 'last_name', 'email']
        password = None
