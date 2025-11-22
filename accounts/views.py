from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UserRegisterForm, LoginForm
from .models import User
from .decorators import role_required


class CustomLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'accounts/login.html'

    def dispatch(self, request, *args, **kwargs):
        # Bloquear login si ya está logueado
        if request.user.is_authenticated:
            # Redirigir al dashboard principal
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Redirige al dashboard después del login"""
        # Redirigir al dashboard principal (ambos roles van al mismo lugar)
        return reverse_lazy('dashboard')  # ✅ Redirige al dashboard de validación
    
    def form_invalid(self, form):
        """Mensaje personalizado cuando el login falla"""
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        """Mensaje de logout exitoso"""
        if request.user.is_authenticated:
            messages.success(request, 'Has cerrado sesión correctamente.')
        return super().dispatch(request, *args, **kwargs)


# ✅ RegisterView solo accesible por admin
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
@method_decorator(role_required(User.ROLE_ADMIN), name='dispatch')
class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        # Si el form no define rol, le pone 'user' por defecto
        if 'role' not in form.cleaned_data:
            form.instance.role = User.ROLE_USER
        messages.success(self.request, 'Usuario registrado exitosamente.')
        return super().form_valid(form)


# ✅ Home de admin — requiere login y rol admin
class AdminHomeView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    login_url = '/accounts/login/'
    template_name = 'accounts/admin_home.html'
    
    def test_func(self):
        """Verificar que el usuario sea admin"""
        return self.request.user.role == User.ROLE_ADMIN
    
    def handle_no_permission(self):
        """Redirigir si no tiene permisos"""
        messages.error(self.request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:user_home')


# ✅ Home de usuario — requiere login
class UserHomeView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    template_name = 'accounts/user_home.html'