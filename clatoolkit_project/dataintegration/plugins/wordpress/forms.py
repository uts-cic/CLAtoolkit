from django import forms


class ConnectForm(forms.Form):
    wp_root = forms.URLField(label="WordPress Root URL")
    client_key = forms.CharField()
    client_secret = forms.CharField()
    unit_id = forms.CharField(widget=forms.HiddenInput())
