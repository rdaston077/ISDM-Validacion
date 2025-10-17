from django.urls import path
from .views import CustomLoginView, CustomLogoutView, RegisterView, AdminHomeView, UserHomeView

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('admin-home/', AdminHomeView.as_view(), name='admin_home'),
    path('user-home/', UserHomeView.as_view(), name='user_home'),
    path('after-login/', AdminHomeView.as_view(), name='after_login'),  # si usás LOGIN_REDIRECT_URL
]
