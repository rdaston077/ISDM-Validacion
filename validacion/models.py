from django.db import models
from django.conf import settings
from django.utils import timezone

class Estado(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre

class TablaSistema(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    importancia = models.IntegerField(default=1)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre

class TipoAccion(models.Model):
    nombre = models.CharField(max_length=50)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    tabla_sistema = models.ForeignKey(TablaSistema, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre

class Permiso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre

class Bitacora(models.Model):
    tipo_accion = models.ForeignKey(TipoAccion, on_delete=models.CASCADE)
    tabla_sistema = models.ForeignKey(TablaSistema, on_delete=models.CASCADE)
    observacion = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    registro_afectado = models.IntegerField()
    valores_nuevos = models.JSONField(blank=True, null=True)
    estado = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.tipo_accion} - {self.tabla_sistema} - {self.fecha}"

class AlertaAdmin(models.Model):
    SEVERIDAD_CHOICES = [
        ('Info', 'Informativa'),
        ('Warning', 'Advertencia'),
        ('Critica', 'Crítica'),
    ]
    
    severidad = models.CharField(max_length=10, choices=SEVERIDAD_CHOICES)
    tabla_sistema = models.ForeignKey(TablaSistema, on_delete=models.CASCADE)
    registro_afectado = models.IntegerField()
    mensaje = models.TextField()
    detalle = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    estado_gestion = models.BooleanField(default=False)
    usuario_asignado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.severidad} - {self.mensaje}"

class Pago(models.Model):
    ESTADOS_PAGO = [
        ('PENDIENTE', 'Pendiente de Validación'),
        ('VALIDADO', 'Validado Correctamente'),
        ('RECHAZADO', 'Rechazado'),
        ('PROCESADO', 'Procesado'),
        ('ERROR', 'Error en Proceso'),
    ]
    
    METODOS_PAGO = [
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('EFECTIVO', 'Efectivo'),
    ]
    
    referencia = models.CharField(max_length=20, unique=True)  # #P-00120
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField()
    fecha_vencimiento = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='PENDIENTE')
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    comision_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    estudiante_nombre = models.CharField(max_length=200)
    concepto = models.CharField(max_length=200)
    comprobante = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    observaciones = models.TextField(blank=True)
    usuario_creacion = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pagos_creados')
    usuario_modificacion = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos_modificados')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.referencia} - ${self.monto}"

class Conciliacion(models.Model):
    ESTADOS_CONCILIACION = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('CONCILIADO', 'Conciliado'),
        ('CON_DIFERENCIAS', 'Con Diferencias'),
    ]
    
    fecha_conciliacion = models.DateField()
    pasarela = models.CharField(max_length=50)  # MacroClick, etc.
    estado = models.CharField(max_length=20, choices=ESTADOS_CONCILIACION, default='PENDIENTE')
    usuario_responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    match_sistema = models.IntegerField(default=0)  # Porcentaje
    diferencias = models.IntegerField(default=0)     # Porcentaje
    sin_match = models.IntegerField(default=0)       # Porcentaje
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Conciliación {self.fecha_conciliacion} - {self.pasarela}"

class Incidencia(models.Model):
    TIPOS_INCIDENCIA = [
        ('DIF_MONTO', 'Diferencia de Monto'),
        ('SIN_MATCH', 'Sin Match'),
        ('DUPLICADO', 'Pago Duplicado'),
        ('MONTO_ALTO', 'Monto Alto'),
        ('AJUSTE', 'Ajuste'),
        ('ANULACION', 'Anulación'),
    ]
    
    ESTADOS_INCIDENCIA = [
        ('ABIERTA', 'Abierta'),
        ('CERRADA', 'Cerrada'),
        ('PENDIENTE_FIRMA', 'Pendiente de Firma'),
    ]
    
    numero_referencia = models.CharField(max_length=20, unique=True)  # #P-00131
    tipo_incidencia = models.CharField(max_length=20, choices=TIPOS_INCIDENCIA)
    estado = models.CharField(max_length=20, choices=ESTADOS_INCIDENCIA, default='ABIERTA')
    descripcion = models.TextField()
    monto_diferencia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pago_relacionado = models.ForeignKey(Pago, on_delete=models.CASCADE, null=True, blank=True)
    conciliacion_relacionada = models.ForeignKey(Conciliacion, on_delete=models.CASCADE, null=True, blank=True)
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    usuario_asignado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    justificacion = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.numero_referencia} - {self.tipo_incidencia}"