from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    # Si no querés que el usuario elija rol, sacá el campo role
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    pass
