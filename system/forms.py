# coding=utf-8
from datetime import time

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import Form
from django.forms.models import ModelForm
from django.forms.widgets import TextInput, NumberInput
from django.utils.translation import ugettext_lazy as _


class RegistrationForm(ModelForm):
    username = forms.SlugField(required=True, label=u"Имя пользователя")
    email = forms.EmailField(required=True, label=u"Email")
    first_name = forms.CharField(required=False, label=u"Имя")
    last_name = forms.CharField(required=False, label=u"Фамилия")
    phone_number = forms.CharField(required=False, label=u"Номер телефона")
    weight = forms.IntegerField(required=False, label=u"Ваш вес")
    height = forms.IntegerField(required=False, label=u"Ваш рост")
    password = forms.CharField(required=True, widget=forms.PasswordInput, label=u"Придумайте пароль")
    password_repeat = forms.CharField(required=True, widget=forms.PasswordInput, label=u"Повторите пароль")

    def clean_password(self):
        password = self.data["password"]
        if len(password) < 8:
            raise ValidationError(u"Пароль должен быть не менее 8 символов")
        return password

    def clean_password_repeat(self):
        if self.data["password"] != self.data["password_repeat"]:
            raise ValidationError(u"Пароли не совпадают")
        return self.data["password_repeat"]

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]