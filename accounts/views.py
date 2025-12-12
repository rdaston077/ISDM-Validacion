from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, FormView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, LoginForm, ProfileEditForm
from validacion.models import Bitacora
from .models import User
from .decorators import role_required

User = get_user_model()

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

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['user_obj'] = user

        # Últimas 3 acciones del usuario (bitácora)
        ultimas = Bitacora.objects.filter(usuario=user).order_by('-fecha')[:3]
        ctx['ultimas_actividades'] = ultimas
        return ctx
    
class ProfileEditView(LoginRequiredMixin, FormView):
    template_name = 'accounts/profile_edit.html'  # o incluir el form en profile.html con POST a esta URL
    form_class = ProfileEditForm
    success_url = reverse_lazy('accounts:profile')
    login_url = '/accounts/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Datos actualizados correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Hubo errores. Revisa el formulario.')
        return super().form_invalid(form)
    
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:password_change_done')
    login_url = '/accounts/login/'

    def form_valid(self, form):
        # actualiza contraseña y mantiene sesión
        response = super().form_valid(form)
        update_session_auth_hash(self.request, form.user)  # importante para no desloguear al usuario
        messages.success(self.request, 'Contraseña actualizada correctamente.')
        return response

    def form_invalid(self, form):
        # se puede usar el mensaje por defecto, pero lo hacemos explícito:
        messages.error(self.request, 'La contraseña actual no es correcta o la nueva no cumple las reglas.')
        return super().form_invalid(form)