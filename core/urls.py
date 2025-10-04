from django.contrib import admin
from django.urls import path
from validacion import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("bitacora/", views.bitacora, name="bitacora"),
    path("conciliacion/", views.conciliacion, name="conciliacion"),
]
