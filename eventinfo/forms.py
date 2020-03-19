from django import forms


class EventSearchForm(forms.Form):
    q = forms.CharField(label='دنبال چی می‌گردی؟', required=False)
    #gi_profile = forms.BooleanField(required=False)

