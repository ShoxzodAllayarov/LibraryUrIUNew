from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'full_name', 'email', 'date_of_birth', 'password1', 'password2')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'username': 'Имя пользователя',
            'full_name': 'Полное имя',
            'email': 'Электронная почта',
            'date_of_birth': 'Дата рождения',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
