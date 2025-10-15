# validation/admin.py
from django.contrib import admin
from .models import Estado, TablaSistema, TipoAccion, Permiso, Bitacora, AlertaAdmin, Pago, Conciliacion, Incidencia

# Registrar todos los modelos
admin.site.register(Estado)
admin.site.register(TablaSistema)
admin.site.register(TipoAccion)
admin.site.register(Permiso)
admin.site.register(Bitacora)
admin.site.register(AlertaAdmin)
admin.site.register(Pago)
admin.site.register(Conciliacion)
admin.site.register(Incidencia)