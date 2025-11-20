# core/urls.py
from django.contrib import admin
from django.urls import include, path
from validacion import views
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("bitacora/", views.bitacora, name="bitacora"),
    path("conciliacion/", views.conciliacion, name="conciliacion"),
    
    # URLs corregidas (con guiones en lugar de underscores):
    path("subir-reporte/", views.subir_reporte_externo, name="subir_reporte_externo"),
    path("generar-incidencias/", views.generar_incidencias, name="generar_incidencias"),
    
    # URLs de pagos:
    path("pagos/", views.lista_pagos, name="lista_pagos"),
    path("pagos/agregar/", views.agregar_pago, name="agregar_pago"),
    
    # ✅ NUEVAS URLs PARA DETALLE Y EDITAR PAGO
    path("pagos/<int:pago_id>/", views.detalle_pago, name="detalle_pago"),
    path("pagos/<int:pago_id>/editar/", views.editar_pago, name="editar_pago"),
    
    # URLs de exportación:
    path("bitacora/exportar-pdf/", views.exportar_bitacora_pdf, name="exportar_bitacora_pdf"),
    path("bitacora/exportar-excel/", views.exportar_bitacora_excel, name="exportar_bitacora_excel"),

    path('exportar-pagos-pdf/', views.exportar_pagos_pdf, name='exportar_pagos_pdf'),
    path('exportar-pagos-excel/', views.exportar_pagos_excel, name='exportar_pagos_excel'),
    
    path('accounts/', include('accounts.urls', namespace='accounts')),

    path('', include('validacion.urls')),
]