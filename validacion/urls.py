from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('bitacora/', views.bitacora, name='bitacora'),
    path('conciliacion/', views.conciliacion, name='conciliacion'),
    
    # Exportaciones
    path('bitacora/exportar-pdf/', views.exportar_bitacora_pdf, name='exportar_bitacora_pdf'),
    path('bitacora/exportar-excel/', views.exportar_bitacora_excel, name='exportar_bitacora_excel'),
    
    # Conciliación
    path('subir-reporte/', views.subir_reporte_externo, name='subir_reporte_externo'),
    path('generar-incidencias/', views.generar_incidencias, name='generar_incidencias'),
    
    # Pagos - AÑADE ESTAS DOS LÍNEAS
    path('pagos/', views.lista_pagos, name='lista_pagos'),
    path('pagos/agregar/', views.agregar_pago, name='agregar_pago'),  # ✅ ESTA FALTA

    path('accounts/', include('accounts.urls')),
]