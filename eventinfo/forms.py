from django import forms
from django.contrib.auth.forms import UserChangeForm

from eventinfo.models import Profile, Event_types


class EventSearchForm(forms.Form):
    q = forms.CharField(label='دنبال چی می‌گردی؟', required=False, widget=forms.TextInput(attrs={'placeholder': "دنبال چی میگردی؟"}))
    event_type = forms.ModelChoiceField(label='دسته‌بندی', queryset=Event_types.objects.all(), empty_label='تمام دسته‌ها', required=False, widget=forms.Select(attrs={'class': "chosen-select"}))
    EVENT_SORT_CHOICES = (
        ('default', 'پیش‌فرض'),
        ('views', 'پربازدید‌ترین‌ها'),
        ('date-desc', 'جدیدترین‌ها'),
        ('date-asc', 'قدیمی‌ترین‌ها'),
        ('featured', 'ویژه'),
        ('rand', 'تصادفی')
    )
    sort = forms.ChoiceField(label='چیدمان', choices=EVENT_SORT_CHOICES, required=False)

    # TODO: filter event city, event price, status, search in title/ desc/ venue/


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['mobile', 'gender', 'bday', 'user_image']


class UserForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = ['first_name', 'last_name', 'email']
        password = None
