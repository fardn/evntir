from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User

from eventinfo.models import Profile, Event_types, Booking


class EventSearchForm(forms.Form):
    q = forms.CharField(label='دنبال چی می‌گردی؟', required=False,
                        widget=forms.TextInput(attrs={'placeholder': "دنبال چی میگردی؟"}))
    event_type = forms.ModelChoiceField(label='دسته‌بندی', queryset=Event_types.objects.all(),
                                        empty_label='تمام دسته‌ها', required=False,
                                        widget=forms.Select(attrs={'class': "chosen-select"}))
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


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            return email

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('This email address is already in use.')
