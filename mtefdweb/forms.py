from django import forms


class FunderEmail(forms.Form):
    email = forms.EmailField()
