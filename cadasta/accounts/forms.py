from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from .models import User
from parsley.decorators import parsleyfy


@parsleyfy
class RegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2',
                  'full_name']

    def clean_username(self):
        username = self.data.get('username')
        if username.lower() in settings.CADASTA_INVALID_ENTITY_NAMES:
            raise forms.ValidationError(
                _("Username cannot be “add” or “new”."))
        return username

    def clean_password1(self):
        password = self.data.get('password1')
        if password != self.data.get('password2'):
            raise forms.ValidationError(_("Passwords do not match"))
        return password

    def clean_email(self):
        email = self.data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("Another user with this email already exists"))
        return email

    def save(self, *args, **kwargs):
        user = super(RegisterForm, self).save(*args, **kwargs)
        user.set_password(self.cleaned_data['password1'])
        user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name']

    def clean_username(self):
        username = self.data.get('username')
        if (self.instance.username != username and
                User.objects.filter(username=username).exists()):
            raise forms.ValidationError(
                _("Another user with this username already exists"))
        if username.lower() in settings.CADASTA_INVALID_ENTITY_NAMES:
            raise forms.ValidationError(
                _("Username cannot be “add” or “new”."))
        return username

    def clean_email(self):
        email = self.data.get('email')
        if (self.instance.email != email and
                User.objects.filter(email=email).exists()):
            raise forms.ValidationError(
                _("Another user with this email already exists"))
        return email
