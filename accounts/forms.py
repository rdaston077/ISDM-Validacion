from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User



class UserRegisterForm(UserCreationForm):
    """
    Formulario de registro de usuario con campos personalizados
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )

    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    )   
   
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        initial=User.ROLE_USER,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Rol'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'role')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Usuario'
            })
        }
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return password2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a los campos de contraseña
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })


class LoginForm(AuthenticationForm):
    """
    Formulario de login con estilos personalizados
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': ' ',  # Espacio vacío para que funcione el label flotante
            'autocomplete': 'username',
            'id': 'username'
        }),
        label='Usuario'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': ' ',  # Espacio vacío para que funcione el label flotante
            'autocomplete': 'current-password',
            'id': 'password'
        }),
        label='Contraseña'
    )
    
    error_messages = {
        'invalid_login': 'Usuario o contraseña incorrectos.',
        'inactive': 'Esta cuenta está inactiva.',
    }