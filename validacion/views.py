from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib.auth.models import User
from accounts.models import User  # ← ESTA ES LA BUENA
from django.core.paginator import Paginator
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import csv
import io
from .models import Pago, Incidencia, Bitacora, Conciliacion, TipoAccion, AlertaAdmin, TablaSistema
from .forms import PagoForm
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from django.contrib.auth.decorators import login_required

@login_required(login_url='/accounts/login/')
def dashboard(request):
    hoy = timezone.now().date()
    
    # KPIs DINÁMICOS
    total_pagos_hoy = Pago.objects.filter(created_at__date=hoy).count()
    incidencias_abiertas = Incidencia.objects.filter(estado='ABIERTA').count()
    firmas_pendientes = Incidencia.objects.filter(estado='PENDIENTE_FIRMA').count()
    
    # Alertas recientes (últimas 24 horas)
    alertas_recientes = Incidencia.objects.filter(
        fecha_apertura__gte=hoy - timedelta(days=1)
    ).order_by('-fecha_apertura')[:3]
    
    # Pendientes de firma
    pendientes_firma = Incidencia.objects.filter(
        estado='PENDIENTE_FIRMA'
    ).order_by('-fecha_apertura')[:3]
    
    # Actividad reciente (bitácora) - Formatear fecha completa
    actividad_bitacora = Bitacora.objects.all().order_by('-fecha')[:3]
    actividad_reciente = []
    for actividad in actividad_bitacora:
        actividad_reciente.append({
            'fecha_hora': actividad.fecha.strftime('%d/%m/%Y %H:%M:%S'),
            'usuario': actividad.usuario.username,
            'accion': actividad.tipo_accion.nombre,
            'objeto': actividad.tabla_sistema.nombre
        })
    
    context = {
        'total_pagos_hoy': total_pagos_hoy,
        'incidencias_abiertas': incidencias_abiertas,
        'firmas_pendientes': firmas_pendientes,
        'alertas_recientes': alertas_recientes,
        'pendientes_firma': pendientes_firma,
        'actividad_reciente': actividad_reciente,
    }
    
    return render(request, 'dashboard.html', context)

# VISTA BITÁCORA COMPLETA
@login_required(login_url='/accounts/login/')
def bitacora(request):
    # Obtener parámetros de filtro
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')
    usuario_filtro = request.GET.get('usuario', '')
    accion_filtro = request.GET.get('accion', '')
    texto_libre = request.GET.get('q', '')
    pagina = request.GET.get('pagina', 1)
    
    # Consulta base
    bitacoras = Bitacora.objects.all().select_related('usuario', 'tipo_accion', 'tabla_sistema').order_by('-fecha')
    
    # Aplicar filtros
    if fecha_desde:
        bitacoras = bitacoras.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        bitacoras = bitacoras.filter(fecha__date__lte=fecha_hasta)
    if usuario_filtro and usuario_filtro != 'Todos':
        bitacoras = bitacoras.filter(usuario__username=usuario_filtro)
    if accion_filtro and accion_filtro != 'Todas':
        bitacoras = bitacoras.filter(tipo_accion__nombre=accion_filtro)
    if texto_libre:
        bitacoras = bitacoras.filter(
            Q(observacion__icontains=texto_libre) |
            Q(valores_nuevos__icontains=texto_libre) |
            Q(usuario__username__icontains=texto_libre) |
            Q(tabla_sistema__nombre__icontains=texto_libre)
        )
    
    # ✅ NUEVO: Formatear registros con fecha completa
    registros_formateados = []
    for bitacora in bitacoras:
        registros_formateados.append({
            'fecha_hora': bitacora.fecha.strftime('%d/%m/%Y %H:%M:%S'),  # Fecha completa
            'usuario': bitacora.usuario.username,
            'accion': bitacora.tipo_accion.nombre,
            'objeto': bitacora.tabla_sistema.nombre,
            'observacion': bitacora.observacion,
            'registro_afectado': bitacora.registro_afectado,
            'valores_nuevos': bitacora.valores_nuevos
        })
    
    # Paginación con registros formateados
    paginator = Paginator(registros_formateados, 20)
    page_obj = paginator.get_page(pagina)
    
    # Estadísticas (usar la consulta original para counts)
    total_registros = bitacoras.count()
    validaciones = bitacoras.filter(tipo_accion__nombre__icontains='VALIDAR').count()
    anulaciones = bitacoras.filter(tipo_accion__nombre__icontains='ANULAR').count()
    alertas = bitacoras.filter(tipo_accion__nombre__icontains='ALERTA').count()
    
    # Obtener opciones para los filtros
    usuarios = User.objects.filter(bitacora__isnull=False).distinct()
    acciones = TipoAccion.objects.all()
    
    context = {
        'bitacoras': page_obj,  # Ahora con fecha formateada
        'total_registros': total_registros,
        'validaciones': validaciones,
        'anulaciones': anulaciones,
        'alertas': alertas,
        'usuarios': usuarios,
        'acciones': acciones,
        'filtros': {
            'desde': fecha_desde,
            'hasta': fecha_hasta,
            'usuario': usuario_filtro,
            'accion': accion_filtro,
            'texto': texto_libre,
        }
    }
    
    return render(request, 'bitacora.html', context)

# EXPORTAR BITÁCORA A PDF
def exportar_bitacora_pdf(request):
    # Obtener los mismos filtros que en la vista bitacora
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')
    usuario_filtro = request.GET.get('usuario', '')
    accion_filtro = request.GET.get('accion', '')
    texto_libre = request.GET.get('q', '')
    
    # Aplicar los mismos filtros
    bitacoras = Bitacora.objects.all().select_related('usuario', 'tipo_accion', 'tabla_sistema').order_by('-fecha')
    
    if fecha_desde:
        bitacoras = bitacoras.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        bitacoras = bitacoras.filter(fecha__date__lte=fecha_hasta)
    if usuario_filtro and usuario_filtro != 'Todos':
        bitacoras = bitacoras.filter(usuario__username=usuario_filtro)
    if accion_filtro and accion_filtro != 'Todas':
        bitacoras = bitacoras.filter(tipo_accion__nombre=accion_filtro)
    if texto_libre:
        bitacoras = bitacoras.filter(
            Q(observacion__icontains=texto_libre) |
            Q(valores_nuevos__icontains=texto_libre) |
            Q(usuario__username__icontains=texto_libre) |
            Q(tabla_sistema__nombre__icontains=texto_libre)
        )
    
    # Crear el PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Bitácora del Sistema - ISDM Validación", styles['Title'])
    elements.append(title)
    
    # Información de filtros
    filtros_text = f"Filtros aplicados: Desde {fecha_desde if fecha_desde else 'N/A'} - Hasta {fecha_hasta if fecha_hasta else 'N/A'} - Usuario: {usuario_filtro if usuario_filtro else 'Todos'} - Acción: {accion_filtro if accion_filtro else 'Todas'}"
    filtros_para = Paragraph(filtros_text, styles['Normal'])
    elements.append(filtros_para)
    
    elements.append(Paragraph("<br/>", styles['Normal']))
    
    # Preparar datos para la tabla
    data = [['Fecha/Hora', 'Usuario', 'Acción', 'Objeto', 'Observación']]
    
    for bitacora in bitacoras:
        fecha_str = bitacora.fecha.strftime('%d/%m/%Y %H:%M:%S')
        data.append([
            fecha_str,
            bitacora.usuario.username,
            bitacora.tipo_accion.nombre,
            bitacora.tabla_sistema.nombre,
            bitacora.observacion[:50] + '...' if len(bitacora.observacion) > 50 else bitacora.observacion
        ])
    
    # Crear tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    elements.append(table)
    
    # Construir PDF
    doc.build(elements)
    
    # Preparar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bitacora_isdm.pdf"'
    
    return response

# EXPORTAR BITÁCORA A EXCEL (CSV)
def exportar_bitacora_excel(request):
    # Obtener los mismos filtros que en la vista bitacora
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')
    usuario_filtro = request.GET.get('usuario', '')
    accion_filtro = request.GET.get('accion', '')
    texto_libre = request.GET.get('q', '')
    
    # Aplicar los mismos filtros
    bitacoras = Bitacora.objects.all().select_related('usuario', 'tipo_accion', 'tabla_sistema').order_by('-fecha')
    
    if fecha_desde:
        bitacoras = bitacoras.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        bitacoras = bitacoras.filter(fecha__date__lte=fecha_hasta)
    if usuario_filtro and usuario_filtro != 'Todos':
        bitacoras = bitacoras.filter(usuario__username=usuario_filtro)
    if accion_filtro and accion_filtro != 'Todas':
        bitacoras = bitacoras.filter(tipo_accion__nombre=accion_filtro)
    if texto_libre:
        bitacoras = bitacoras.filter(
            Q(observacion__icontains=texto_libre) |
            Q(valores_nuevos__icontains=texto_libre) |
            Q(usuario__username__icontains=texto_libre) |
            Q(tabla_sistema__nombre__icontains=texto_libre)
        )
    
    # Crear respuesta CSV (simulando Excel)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bitacora_isdm.csv"'
    
    writer = csv.writer(response)
    # Escribir encabezados
    writer.writerow(['Fecha/Hora', 'Usuario', 'Acción', 'Objeto', 'Observación', 'Valores Nuevos', 'Registro Afectado'])
    
    # Escribir datos
    for bitacora in bitacoras:
        fecha_str = bitacora.fecha.strftime('%d/%m/%Y %H:%M:%S')
        writer.writerow([
            fecha_str,
            bitacora.usuario.username,
            bitacora.tipo_accion.nombre,
            bitacora.tabla_sistema.nombre,
            bitacora.observacion,
            str(bitacora.valores_nuevos) if bitacora.valores_nuevos else '',
            bitacora.registro_afectado
        ])
    
    return response

# VISTA CONCILIACIÓN COMPLETA
@login_required(login_url='/accounts/login/')
def conciliacion(request):
    # Obtener parámetros del formulario
    fecha_conciliacion = request.GET.get('fecha', '')
    pasarela_filtro = request.GET.get('pasarela', 'MacroClick')
    
    # Consulta base para pagos del sistema
    pagos_sistema = Pago.objects.all().order_by('-created_at')
    
    # Si hay fecha, filtrar por fecha
    if fecha_conciliacion:
        pagos_sistema = pagos_sistema.filter(created_at__date=fecha_conciliacion)
    
    # Simular datos externos (esto luego vendrá de archivos CSV)
    datos_externos = [
        {'referencia': '#P-00120', 'monto': 10000, 'origen': 'Tarjeta', 'estado': 'OK'},
        {'referencia': '#P-00121', 'monto': 10000, 'origen': 'Tarjeta', 'estado': 'DIF'},
        {'referencia': '', 'monto': '', 'origen': '', 'estado': 'SIN_MATCH'},
    ]
    
    # Procesar matching y estados
    for pago in pagos_sistema:
        pago.estado_conciliacion = 'SIN_MATCH'  # Por defecto
        pago.monto_externo = None
        
        for externo in datos_externos:
            if externo['referencia'] == pago.referencia:
                if externo['monto'] == float(pago.monto):
                    pago.estado_conciliacion = 'OK'
                else:
                    pago.estado_conciliacion = 'DIF'
                    pago.monto_externo = externo['monto']
                break
    
    # Estadísticas
    total_pagos = pagos_sistema.count()
    pagos_ok = sum(1 for p in pagos_sistema if getattr(p, 'estado_conciliacion', '') == 'OK')
    pagos_dif = sum(1 for p in pagos_sistema if getattr(p, 'estado_conciliacion', '') == 'DIF')
    pagos_sin_match = sum(1 for p in pagos_sistema if getattr(p, 'estado_conciliacion', '') == 'SIN_MATCH')
    
    context = {
        'pagos_sistema': pagos_sistema,
        'datos_externos': datos_externos,
        'total_pagos': total_pagos,
        'pagos_ok': pagos_ok,
        'pagos_dif': pagos_dif,
        'pagos_sin_match': pagos_sin_match,
        'filtros': {
            'fecha': fecha_conciliacion,
            'pasarela': pasarela_filtro,
        }
    }
    
    return render(request, 'conciliacion.html', context)


def subir_reporte_externo(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        # Aquí procesarías el archivo CSV y guardarías los datos
        # Por ahora solo redirigimos
        return redirect('conciliacion')
    return redirect('conciliacion')

def generar_incidencias(request):
    if request.method == 'POST':
        # Lógica para generar incidencias automáticamente
        pagos_sistema = Pago.objects.all()
        
        for pago in pagos_sistema:
            # Simular lógica de detección de diferencias
            if pago.referencia == '#P-00121':  # Ejemplo de pago con diferencia
                Incidencia.objects.create(
                    numero_referencia=f"DIF-{pago.referencia}",
                    tipo_incidencia='DIF_MONTO',
                    descripcion=f"Diferencia detectada en {pago.referencia}",
                    pago_relacionado=pago,
                    monto_diferencia=200  # Ejemplo: 10,000 vs 9,800
                )
            elif pago.referencia == '#P-00122':  # Ejemplo de pago sin match
                Incidencia.objects.create(
                    numero_referencia=f"SM-{pago.referencia}",
                    tipo_incidencia='SIN_MATCH',
                    descripcion=f"Pago sin match externo: {pago.referencia}",
                    pago_relacionado=pago
                )
        
        return redirect('conciliacion')
    return redirect('conciliacion')

@login_required(login_url='/accounts/login/')
def lista_pagos(request):
    # Obtener parámetros de filtro
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')
    estado_filtro = request.GET.get('estado', 'Todos')
    metodo_filtro = request.GET.get('metodo', 'Todos')
    texto_libre = request.GET.get('q', '')
    pagina = request.GET.get('pagina', 1)
    
    # Consulta base
    pagos = Pago.objects.all().order_by('-created_at')
    
    # Aplicar filtros
    if fecha_desde:
        pagos = pagos.filter(fecha_pago__date__gte=fecha_desde)
    if fecha_hasta:
        pagos = pagos.filter(fecha_pago__date__lte=fecha_hasta)
    if estado_filtro and estado_filtro != 'Todos':
        pagos = pagos.filter(estado=estado_filtro)
    if metodo_filtro and metodo_filtro != 'Todos':
        pagos = pagos.filter(metodo_pago=metodo_filtro)
    if texto_libre:
        pagos = pagos.filter(
            Q(referencia__icontains=texto_libre) |
            Q(estudiante_nombre__icontains=texto_libre) |
            Q(concepto__icontains=texto_libre)
        )
    
    # Paginación
    paginator = Paginator(pagos, 20)
    page_obj = paginator.get_page(pagina)
    
    # Estadísticas para las tarjetas (usar consulta filtrada)
    total_pagos = pagos.count()
    pagos_pagados = pagos.filter(estado='PAGADO').count()
    pagos_pendientes = pagos.filter(estado='PENDIENTE').count()
    pagos_vencidos = pagos.filter(estado='VENCIDO').count()
    
    context = {
        'pagos': page_obj,
        'total_pagos': total_pagos,
        'pagos_pagados': pagos_pagados,
        'pagos_pendientes': pagos_pendientes,
        'pagos_vencidos': pagos_vencidos,
        'filtros': {
            'desde': fecha_desde,
            'hasta': fecha_hasta,
            'estado': estado_filtro,
            'metodo': metodo_filtro,
            'texto': texto_libre,
        }
    }
    
    return render(request, 'lista_pagos.html', context)

# NUEVA FUNCIÓN PARA AGREGAR PAGOS
def agregar_pago(request):
    if request.method == 'POST':
        form = PagoForm(request.POST, request.FILES)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.usuario_creacion = request.user
            
            # Combinar fecha y hora en los campos DateTime
            fecha_pago = form.cleaned_data['fecha_pago']
            hora_pago = form.cleaned_data['hora_pago']
            pago.fecha_pago = datetime.combine(fecha_pago, hora_pago)
            
            fecha_vencimiento = form.cleaned_data['fecha_vencimiento']
            hora_vencimiento = form.cleaned_data['hora_vencimiento']
            pago.fecha_vencimiento = datetime.combine(fecha_vencimiento, hora_vencimiento)
            
            pago.save()
            
            # Registrar en bitácora (si las tablas existen)
            try:
                tipo_accion, created = TipoAccion.objects.get_or_create(
                    nombre='CREAR_PAGO',
                    defaults={'estado_id': 1, 'tabla_sistema_id': 1}
                )
                tabla_sistema, created = TablaSistema.objects.get_or_create(
                    nombre='Pagos',
                    defaults={'descripcion': 'Tabla de pagos del sistema', 'importancia': 1, 'estado_id': 1}
                )
                
                Bitacora.objects.create(
                    tipo_accion=tipo_accion,
                    tabla_sistema=tabla_sistema,
                    observacion=f"Pago creado: {pago.referencia} - {pago.estudiante_nombre} - ${pago.monto}",
                    usuario=request.user,
                    registro_afectado=pago.id
                )
            except Exception as e:
                # Si hay error con la bitácora, continuar igual
                print(f"Error al registrar en bitácora: {e}")
            
            # Determinar a dónde redirigir según el botón presionado
            if 'guardar_agregar_otro' in request.POST:
                return redirect('agregar_pago')
            elif 'guardar_continuar' in request.POST:
                # En un futuro podrías crear una vista de edición
                return redirect('lista_pagos')
            else:
                return redirect('lista_pagos')
    else:
        form = PagoForm()
    
    # ✅ CORREGIDO: Usar 'pago.html' en lugar de 'pagos_cuotas.html'
    return render(request, 'pago.html', {'form': form})

def exportar_pagos_pdf(request):
    # Obtener parámetros de filtro (igual que en lista_pagos)
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')
    estado_filtro = request.GET.get('estado', 'Todos')
    metodo_filtro = request.GET.get('metodo', 'Todos')
    texto_libre = request.GET.get('q', '')
    
    # Consulta base
    pagos = Pago.objects.all().order_by('-created_at')
    
    # Aplicar filtros
    if fecha_desde:
        pagos = pagos.filter(fecha_pago__date__gte=fecha_desde)
    if fecha_hasta:
        pagos = pagos.filter(fecha_pago__date__lte=fecha_hasta)
    if estado_filtro and estado_filtro != 'Todos':
        pagos = pagos.filter(estado=estado_filtro)
    if metodo_filtro and metodo_filtro != 'Todos':
        pagos = pagos.filter(metodo_pago=metodo_filtro)
    if texto_libre:
        pagos = pagos.filter(
            Q(referencia__icontains=texto_libre) |
            Q(estudiante_nombre__icontains=texto_libre) |
            Q(concepto__icontains=texto_libre)
        )
    
    # Crear el PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Reporte de Pagos - ISDM Validación", styles['Title'])
    elements.append(title)
    
    # Información de filtros
    filtros_lista = []
    if fecha_desde: filtros_lista.append(f"Desde: {fecha_desde}")
    if fecha_hasta: filtros_lista.append(f"Hasta: {fecha_hasta}")
    if estado_filtro != 'Todos': filtros_lista.append(f"Estado: {estado_filtro}")
    if metodo_filtro != 'Todos': filtros_lista.append(f"Método: {metodo_filtro}")
    if texto_libre: filtros_lista.append(f"Búsqueda: {texto_libre}")
    
    if filtros_lista:
        filtros_text = "Filtros aplicados: " + " | ".join(filtros_lista)
        filtros_para = Paragraph(filtros_text, styles['Normal'])
        elements.append(filtros_para)
    
    elements.append(Paragraph("<br/>", styles['Normal']))
    
    # Preparar datos para la tabla
    data = [['Referencia', 'Estudiante', 'Monto', 'Fecha Pago', 'Concepto', 'Estado', 'Método']]
    
    for pago in pagos:
        data.append([
            pago.referencia,
            pago.estudiante_nombre,
            f"${pago.monto:,.2f}",
            pago.fecha_pago.strftime('%d/%m/%Y %H:%M') if pago.fecha_pago else '',
            pago.concepto,
            pago.estado,
            pago.metodo_pago
        ])
    
    # Crear tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    elements.append(table)
    
    # Estadísticas resumen
    elements.append(Paragraph("<br/>", styles['Normal']))
    total_monto = sum(pago.monto for pago in pagos)
    resumen_text = f"Total registros: {pagos.count()} | Monto total: ${total_monto:,.2f}"
    resumen_para = Paragraph(resumen_text, styles['Normal'])
    elements.append(resumen_para)
    
    # Pie de página
    elements.append(Paragraph(f"<br/>Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    
    # Construir PDF
    doc.build(elements)
    
    # Preparar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_pagos.pdf"'
    
    return response

def exportar_pagos_excel(request):
    # Obtener parámetros de filtro (igual que en lista_pagos)
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')
    estado_filtro = request.GET.get('estado', 'Todos')
    metodo_filtro = request.GET.get('metodo', 'Todos')
    texto_libre = request.GET.get('q', '')
    
    # Consulta base
    pagos = Pago.objects.all().order_by('-created_at')
    
    # Aplicar filtros
    if fecha_desde:
        pagos = pagos.filter(fecha_pago__date__gte=fecha_desde)
    if fecha_hasta:
        pagos = pagos.filter(fecha_pago__date__lte=fecha_hasta)
    if estado_filtro and estado_filtro != 'Todos':
        pagos = pagos.filter(estado=estado_filtro)
    if metodo_filtro and metodo_filtro != 'Todos':
        pagos = pagos.filter(metodo_pago=metodo_filtro)
    if texto_libre:
        pagos = pagos.filter(
            Q(referencia__icontains=texto_libre) |
            Q(estudiante_nombre__icontains=texto_libre) |
            Q(concepto__icontains=texto_libre)
        )
    
    # Crear libro de Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Pagos"
    
    # Título
    ws.merge_cells('A1:G1')
    ws['A1'] = "Reporte de Pagos - ISDM Validación"
    ws['A1'].font = Font(size=16, bold=True)
    ws['A1'].alignment = Alignment(horizontal='center')
    
    # Información de filtros
    row_num = 3
    filtros_lista = []
    if fecha_desde: filtros_lista.append(f"Desde: {fecha_desde}")
    if fecha_hasta: filtros_lista.append(f"Hasta: {fecha_hasta}")
    if estado_filtro != 'Todos': filtros_lista.append(f"Estado: {estado_filtro}")
    if metodo_filtro != 'Todos': filtros_lista.append(f"Método: {metodo_filtro}")
    if texto_libre: filtros_lista.append(f"Búsqueda: {texto_libre}")
    
    if filtros_lista:
        ws.merge_cells(f'A{row_num}:G{row_num}')
        ws[f'A{row_num}'] = "Filtros aplicados: " + " | ".join(filtros_lista)
        ws[f'A{row_num}'].font = Font(italic=True)
        row_num += 2
    
    # Encabezados de tabla
    headers = ['Referencia', 'Estudiante', 'Monto', 'Fecha Pago', 'Concepto', 'Estado', 'Método']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=row_num, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
        cell.fill = PatternFill(start_color='343a40', end_color='343a40', fill_type='solid')
        cell.font = Font(color='FFFFFF', bold=True)
    
    # Datos
    for pago in pagos:
        row_num += 1
        ws.cell(row=row_num, column=1, value=pago.referencia)
        ws.cell(row=row_num, column=2, value=pago.estudiante_nombre)
        ws.cell(row=row_num, column=3, value=float(pago.monto))
        ws.cell(row=row_num, column=4, value=pago.fecha_pago.strftime('%d/%m/%Y %H:%M') if pago.fecha_pago else '')
        ws.cell(row=row_num, column=5, value=pago.concepto)
        ws.cell(row=row_num, column=6, value=pago.estado)
        ws.cell(row=row_num, column=7, value=pago.metodo_pago)
    
    # Formato de moneda para la columna de monto
    for row in range(row_num - pagos.count() + 1, row_num + 1):
        ws.cell(row=row, column=3).number_format = '"$"#,##0.00'
    
    # Estadísticas resumen
    row_num += 2
    total_monto = sum(pago.monto for pago in pagos)
    ws.merge_cells(f'A{row_num}:G{row_num}')
    ws[f'A{row_num}'] = f"Total registros: {pagos.count()} | Monto total: ${total_monto:,.2f}"
    ws[f'A{row_num}'].font = Font(bold=True)
    
    # Fecha de generación
    row_num += 1
    ws.merge_cells(f'A{row_num}:G{row_num}')
    ws[f'A{row_num}'] = f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws[f'A{row_num}'].font = Font(italic=True)
    
    # Ajustar anchos de columna
    column_widths = {
        'A': 20,  # Referencia
        'B': 25,  # Estudiante
        'C': 15,  # Monto
        'D': 20,  # Fecha Pago
        'E': 30,  # Concepto
        'F': 15,  # Estado
        'G': 15   # Método
    }
    
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width
    
    # Guardar en buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    # Crear respuesta
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="reporte_pagos.xlsx"'
    
    return response