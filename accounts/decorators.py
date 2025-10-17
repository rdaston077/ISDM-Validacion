from django.contrib.auth.decorators import user_passes_test

def role_required(role):
    def check(user):
        return user.is_authenticated and getattr(user, 'role', None) == role
    return user_passes_test(check, login_url='accounts:login')
