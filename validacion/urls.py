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
    
    # Conciliación - CORREGIDAS Y SIN DUPLICADOS
     path('conciliacion/subir-reporte/', views.subir_reporte_externo, name='subir_reporte_externo'),
    path('conciliacion/generar-incidencias/', views.generar_incidencias, name='generar_incidencias'),
    path('conciliacion/generar-arqueo/', views.generar_arqueo, name='generar_arqueo'),
    path('conciliacion/conciliar-seleccionados/', views.conciliar_seleccionados, name='conciliar_seleccionados'),
    path('conciliacion/resolver-diferencia/', views.resolver_diferencia, name='resolver_diferencia'),  
    
    # PAGOS
    path('pagos/', views.lista_pagos, name='lista_pagos'),
    path('pago/agregar/', views.agregar_pago, name='agregar_pago'),
    path('pago/<int:pago_id>/', views.detalle_pago, name='detalle_pago'),
    path('pago/editar/<int:pago_id>/', views.editar_pago, name='editar_pago'),
    path('pago/eliminar/<int:pago_id>/', views.eliminar_pago, name='eliminar_pago'),
    
    # Incidencias
    path('pago/<int:pago_id>/incidencia/crear/', views.crear_incidencia, name='crear_incidencia'),
    
    # Exportaciones de pagos
    path('pagos/exportar-pdf/', views.exportar_pagos_pdf, name='exportar_pagos_pdf'),
    path('pagos/exportar-excel/', views.exportar_pagos_excel, name='exportar_pagos_excel'),
    
    path('accounts/', include('accounts.urls')),
]