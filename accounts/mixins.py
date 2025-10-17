from django.contrib.auth.mixins import AccessMixin

class RoleRequiredMixin(AccessMixin):
    required_role = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.required_role and getattr(request.user, 'role', None) != self.required_role:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
