from django.db import models

# Create your models here.
from django.db import models

class BitacoraAccion(models.Model):
    fecha_hora = models.DateTimeField(auto_now_add=True)
    usuario    = models.CharField(max_length=100)
    ip         = models.GenericIPAddressField(null=True, blank=True)
    accion     = models.CharField(max_length=50)  # VALIDAR_PAGO, ANULAR_PAGO, ALERTA_DIF...
    objeto_ref = models.CharField(max_length=50)  # p.ej. #P-00123
    justificacion = models.TextField(blank=True)
    class Meta: ordering = ["-fecha_hora"]

class Incidencia(models.Model):
    TIPO   = [("DIF_MONTO","Dif monto"),("SIN_MATCH","Sin match"),("DUPLICADO","Duplicado")]
    ESTADO = [("ABIERTA","Abierta"),("EN_ANALISIS","En análisis"),("RESUELTA","Resuelta")]
    tipo = models.CharField(max_length=20, choices=TIPO)
    referencia = models.CharField(max_length=50)  # #P-00121
    monto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    detalle = models.TextField(blank=True)
    estado = models.CharField(max_length=12, choices=ESTADO, default="ABIERTA")
    responsable = models.CharField(max_length=100, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

class ArqueoDiario(models.Model):
    fecha = models.DateField(unique=True)
    total_interno = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_externo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)
    generado_por  = models.CharField(max_length=100)

class ReglaPermiso(models.Model):
    accion         = models.CharField(max_length=50)   # ej. ANULAR_PAGO
    requiere_firma = models.BooleanField(default=False)
    monto_umbral   = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    activo         = models.BooleanField(default=True)

from django.db import models

class BitacoraAccion(models.Model):
    fecha_hora = models.DateTimeField(auto_now_add=True)
    usuario    = models.CharField(max_length=100)
    ip         = models.GenericIPAddressField(null=True, blank=True)
    accion     = models.CharField(max_length=50)  # VALIDAR_PAGO, ANULAR_PAGO, ALERTA_DIF...
    objeto_ref = models.CharField(max_length=50)  # p.ej. #P-00123
    justificacion = models.TextField(blank=True)
    class Meta: ordering = ["-fecha_hora"]

class Incidencia(models.Model):
    TIPO   = [("DIF_MONTO","Dif monto"),("SIN_MATCH","Sin match"),("DUPLICADO","Duplicado")]
    ESTADO = [("ABIERTA","Abierta"),("EN_ANALISIS","En análisis"),("RESUELTA","Resuelta")]
    tipo = models.CharField(max_length=20, choices=TIPO)
    referencia = models.CharField(max_length=50)  # #P-00121
    monto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    detalle = models.TextField(blank=True)
    estado = models.CharField(max_length=12, choices=ESTADO, default="ABIERTA")
    responsable = models.CharField(max_length=100, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

class ArqueoDiario(models.Model):
    fecha = models.DateField(unique=True)
    total_interno = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_externo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)
    generado_por  = models.CharField(max_length=100)

class ReglaPermiso(models.Model):
    accion         = models.CharField(max_length=50)   # ej. ANULAR_PAGO
    requiere_firma = models.BooleanField(default=False)
    monto_umbral   = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    activo         = models.BooleanField(default=True)
