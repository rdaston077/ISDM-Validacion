from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .forms import UserRegisterForm, LoginForm
from .models import User
from .decorators import role_required


class CustomLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        if getattr(user, 'role', None) == User.ROLE_ADMIN:
            return '/'  # Si es admin, va al inicio
        return '/'      # Si es usuario común, también por ahora


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')


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
        return super().form_valid(form)


# ✅ Home de admin y usuario — ambas requieren login
class AdminHomeView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    template_name = 'accounts/admin_home.html'


class UserHomeView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    template_name = 'accounts/user_home.html'
