# validacion/urls.py
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
    
    # Pagos
    path('pagos/', views.lista_pagos, name='lista_pagos'),
    path('pagos/agregar/', views.agregar_pago, name='agregar_pago'),
    
    # ✅ NUEVAS URLs PARA DETALLE Y EDITAR PAGO
    path('pagos/<int:pago_id>/', views.detalle_pago, name='detalle_pago'),
    path('pagos/<int:pago_id>/editar/', views.editar_pago, name='editar_pago'),
    
    # Exportaciones de pagos
    path('pagos/exportar-pdf/', views.exportar_pagos_pdf, name='exportar_pagos_pdf'),
    path('pagos/exportar-excel/', views.exportar_pagos_excel, name='exportar_pagos_excel'),
    
    path('accounts/', include('accounts.urls')),

]