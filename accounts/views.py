from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UserRegisterForm, LoginForm
from .models import User

class CustomLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        if getattr(user, 'role', None) == User.ROLE_ADMIN:
            return '/'  # Admin va a raíz
        return '/'      # User también va a raíz (mismo lugar)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')  # ← Si ya está logueado va a raíz
        return super().dispatch(request, *args, **kwargs)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')

class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        # si no querés que role venga del form, forzalo acá:
        if 'role' not in form.cleaned_data:
            form.instance.role = User.ROLE_USER
        return super().form_valid(form)

# Home views simples para redirección
class AdminHomeView(TemplateView):
    template_name = 'accounts/admin_home.html'

class UserHomeView(TemplateView):
    template_name = 'accounts/user_home.html'
