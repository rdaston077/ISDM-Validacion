# generar_datos_prueba.py - VERSIÓN COMPLETAMENTE CORREGIDA
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from accounts.models import User
from validacion.models import (
    Estado, TablaSistema, TipoAccion, 
    Bitacora, Pago, Incidencia, Conciliacion, AlertaAdmin
)

def limpiar_datos_existentes():
    """Limpiar datos existentes para evitar duplicados"""
    print("🧹 LIMPIANDO DATOS EXISTENTES...")
    try:
        Pago.objects.all().delete()
        Incidencia.objects.all().delete()
        AlertaAdmin.objects.all().delete()
        Conciliacion.objects.all().delete()
        Bitacora.objects.all().delete()
        print("✅ Datos anteriores eliminados")
    except Exception as e:
        print(f"⚠️ Error limpiando datos: {e}")

def crear_estados():
    print("Creando estados...")
    estados = [
        ('Activo', 'Registro activo en el sistema'),
        ('Inactivo', 'Registro inactivo en el sistema'),
        ('Suspendido', 'Registro temporalmente suspendido'),
    ]
    
    for nombre, descripcion in estados:
        Estado.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': descripcion}
        )
    print(f"✅ Estados creados: {Estado.objects.count()}")

def crear_tablas_sistema():
    print("Creando tablas del sistema...")
    estado_activo = Estado.objects.get(nombre='Activo')
    
    tablas = [
        ('Pagos', 'Tabla de registros de pagos', 5),
        ('Incidencias', 'Tabla de incidencias del sistema', 4),
        ('Usuarios', 'Tabla de usuarios del sistema', 3),
        ('Conciliaciones', 'Tabla de procesos de conciliacion', 4),
        ('Alertas', 'Tabla de alertas administrativas', 4),
    ]
    
    for nombre, descripcion, importancia in tablas:
        TablaSistema.objects.get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': descripcion,
                'importancia': importancia,
                'estado': estado_activo
            }
        )
    print(f"✅ Tablas sistema creadas: {TablaSistema.objects.count()}")

def crear_tipos_accion():
    print("Creando tipos de acción...")
    estado_activo = Estado.objects.get(nombre='Activo')
    tabla_pagos = TablaSistema.objects.get(nombre='Pagos')
    tabla_incidencias = TablaSistema.objects.get(nombre='Incidencias')
    tabla_alertas = TablaSistema.objects.get(nombre='Alertas')
    
    acciones = [
        ('CREAR_PAGO', tabla_pagos),
        ('VALIDAR_PAGO', tabla_pagos),
        ('ANULAR_PAGO', tabla_pagos), 
        ('MODIFICAR_PAGO', tabla_pagos),
        ('CONCILIAR_PAGO', tabla_pagos),
        ('CREAR_INCIDENCIA', tabla_incidencias),
        ('RESOLVER_INCIDENCIA', tabla_incidencias),
        ('GENERAR_ALERTA', tabla_alertas),
    ]
    
    for accion, tabla in acciones:
        TipoAccion.objects.get_or_create(
            nombre=accion,
            defaults={
                'estado': estado_activo,
                'tabla_sistema': tabla
            }
        )
    print(f"✅ Tipos acción creados: {TipoAccion.objects.count()}")

def crear_usuarios():
    print("Creando usuarios...")
    
    usuarios = [
        ('admin', 'admin@institutomilagro.edu.ar', 'Administrador', True),
        ('mlopez', 'mlopez@institutomilagro.edu.ar', 'Monica Lopez', True),
        ('jdiaz', 'jdiaz@institutomilagro.edu.ar', 'Juan Diaz', True),
        ('pgomez', 'pgomez@institutomilagro.edu.ar', 'Pedro Gomez', True),
        ('sistema', 'sistema@institutomilagro.edu.ar', 'Sistema Automatico', False),
    ]
    
    for username, email, nombre, is_staff in usuarios:
        # Verificar si el usuario ya existe para evitar duplicados
        if not User.objects.filter(username=username).exists():
            user = User.objects.create(
                username=username,
                email=email,
                first_name=nombre.split()[0],
                last_name=nombre.split()[1] if len(nombre.split()) > 1 else '',
                is_staff=is_staff,
                is_active=True
            )
            user.set_password('password123')
            user.save()
            print(f"👤 Usuario creado: {username}")
        else:
            print(f"👤 Usuario ya existe: {username}")
    
    print(f"✅ Usuarios listos: {User.objects.count()}")

def crear_pagos():
    print("Creando pagos de prueba...")
    usuario_admin = User.objects.get(username='admin')
    usuario_mlopez = User.objects.get(username='mlopez')
    
    # Valores de cuotas
    valores_cuotas = {
        'ENERO': 98000, 'FEBRERO': 98000, 'MARZO': 106000, 'ABRIL': 106000, 
        'MAYO': 106000, 'JUNIO': 106000, 'JULIO': 106000, 'AGOSTO': 106000,
        'SEPTIEMBRE': 106000, 'OCTUBRE': 110000, 'NOVIEMBRE': 110000, 'DICIEMBRE': 110000,
    }
    
    estudiantes = [
        'Juan Perez', 'Maria Gonzalez', 'Carlos Lopez', 
        'Ana Martinez', 'Pedro Rodriguez', 'Laura Fernandez',
        'Miguel Sanchez', 'Sofia Ramirez', 'Diego Torres', 'Elena Castro'
    ]
    
    metodos_pago = ['TARJETA', 'TRANSFERENCIA', 'EFECTIVO']
    estados_pago = ['PENDIENTE', 'VALIDADO', 'PROCESADO', 'RECHAZADO']
    usuarios_creacion = [usuario_admin, usuario_mlopez]
    
    pago_id = 100
    pagos_creados = 0
    
    for mes, monto in valores_cuotas.items():
        for estudiante in estudiantes:
            try:
                # Crear variaciones realistas
                monto_variado = monto
                if random.random() > 0.8:
                    monto_variado = monto - random.randint(1000, 5000)
                
                mes_numero = list(valores_cuotas.keys()).index(mes) + 1
                fecha_pago = timezone.now().replace(
                    year=2024, month=mes_numero, 
                    day=random.randint(1, 28), hour=12, minute=0, second=0, microsecond=0
                )
                
                fecha_vencimiento = timezone.now().replace(
                    year=2024, month=mes_numero, day=10, hour=0, minute=0, second=0, microsecond=0
                )
                
                estado = random.choices(estados_pago, weights=[0.2, 0.6, 0.15, 0.05])[0]
                
                # Usar create() en lugar de get_or_create para evitar duplicados
                Pago.objects.create(
                    referencia=f"#P-{pago_id:05d}",
                    monto=monto_variado,
                    fecha_pago=fecha_pago,
                    fecha_vencimiento=fecha_vencimiento,
                    estado=estado,
                    estudiante_nombre=estudiante,
                    concepto=f'Cuota {mes} 2024',
                    metodo_pago=random.choice(metodos_pago),
                    comision_porcentaje=random.choice([0, 1.5, 2.0, 3.0]),
                    usuario_creacion=random.choice(usuarios_creacion),
                )
                pagos_creados += 1
                pago_id += 1
                
            except Exception as e:
                print(f"❌ Error creando pago {pago_id}: {e}")
                pago_id += 1  # Incrementar igual para evitar referencias duplicadas
                continue
    
    print(f"✅ Pagos creados: {pagos_creados}")

def crear_incidencias():
    print("Creando incidencias...")
    usuario_admin = User.objects.get(username='admin')
    usuario_mlopez = User.objects.get(username='mlopez')
    usuario_jdiaz = User.objects.get(username='jdiaz')
    
    # Obtener pagos para relacionar
    pagos = list(Pago.objects.all())
    
    if not pagos:
        print("❌ No hay pagos para crear incidencias")
        return
    
    incidencias_creadas = 0
    
    # Crear incidencias basadas en pagos reales
    for i in range(min(15, len(pagos))):
        pago = pagos[i]
        try:
            Incidencia.objects.create(
                numero_referencia=f'DIF-{i+1:03d}',
                tipo_incidencia='DIF_MONTO',
                estado=random.choice(['ABIERTA', 'PENDIENTE_FIRMA']),
                descripcion=f'Diferencia detectada en {pago.referencia} - {random.choice(["MacroClick", "PagoFacil"])}',
                monto_diferencia=random.randint(500, 3000),
                pago_relacionado=pago,
                usuario_asignado=random.choice([usuario_mlopez, usuario_jdiaz])
            )
            incidencias_creadas += 1
        except Exception as e:
            print(f"❌ Error creando incidencia DIF-{i+1:03d}: {e}")
    
    # Incidencias sin match
    for i in range(5):
        try:
            Incidencia.objects.create(
                numero_referencia=f'SM-{i+1:03d}',
                tipo_incidencia='SIN_MATCH',
                estado='ABIERTA',
                descripcion=f'Transferencia sin match - Ref: TRF-{random.randint(100000, 999999)}',
                usuario_asignado=usuario_mlopez
            )
            incidencias_creadas += 1
        except Exception as e:
            print(f"❌ Error creando incidencia SM-{i+1:03d}: {e}")
    
    print(f"✅ Incidencias creadas: {incidencias_creadas}")

def crear_bitacora():
    print("Creando bitácora...")
    try:
        tabla_pagos = TablaSistema.objects.get(nombre='Pagos')
        tabla_incidencias = TablaSistema.objects.get(nombre='Incidencias')
        tabla_alertas = TablaSistema.objects.get(nombre='Alertas')
        
        usuario_admin = User.objects.get(username='admin')
        usuario_mlopez = User.objects.get(username='mlopez')
        usuario_sistema = User.objects.get(username='sistema')
        
        tipos_accion = {ta.nombre: ta for ta in TipoAccion.objects.all()}
        pagos = list(Pago.objects.all()[:10])
        incidencias = list(Incidencia.objects.all()[:5])
        
        bitacora_creada = 0
        
        # Registros de pagos
        for pago in pagos:
            try:
                Bitacora.objects.create(
                    tipo_accion=tipos_accion['CREAR_PAGO'],
                    tabla_sistema=tabla_pagos,
                    observacion=f'Pago creado: {pago.referencia}',
                    usuario=pago.usuario_creacion,
                    registro_afectado=pago.id,
                    valores_nuevos={
                        'referencia': pago.referencia,
                        'monto': str(pago.monto),
                        'estudiante': pago.estudiante_nombre
                    },
                    estado=True
                )
                bitacora_creada += 1
            except Exception as e:
                print(f"❌ Error creando bitácora pago: {e}")
        
        # Registros de incidencias
        for incidencia in incidencias:
            try:
                Bitacora.objects.create(
                    tipo_accion=tipos_accion['CREAR_INCIDENCIA'],
                    tabla_sistema=tabla_incidencias,
                    observacion=f'Incidencia creada: {incidencia.numero_referencia}',
                    usuario=usuario_sistema,
                    registro_afectado=incidencia.id,
                    valores_nuevos={
                        'numero_referencia': incidencia.numero_referencia,
                        'tipo': incidencia.tipo_incidencia
                    },
                    estado=True
                )
                bitacora_creada += 1
            except Exception as e:
                print(f"❌ Error creando bitácora incidencia: {e}")
        
        print(f"✅ Bitácora creada: {bitacora_creada} registros")
        
    except Exception as e:
        print(f"❌ Error en bitácora: {e}")

def crear_conciliaciones():
    print("Creando conciliaciones...")
    usuario_admin = User.objects.get(username='admin')
    conciliaciones_creadas = 0
    
    for i in range(7):
        fecha = timezone.now().date() - timedelta(days=i)
        try:
            Conciliacion.objects.create(
                fecha_conciliacion=fecha,
                pasarela=random.choice(['MacroClick', 'PagoFacil', 'Banco Nacion']),
                estado=random.choice(['CONCILIADO', 'CON_DIFERENCIAS']),
                usuario_responsable=usuario_admin,
                match_sistema=random.randint(75, 95),
                diferencias=random.randint(3, 15),
                sin_match=random.randint(2, 10)
            )
            conciliaciones_creadas += 1
        except Exception as e:
            print(f"❌ Error creando conciliación: {e}")
    
    print(f"✅ Conciliaciones creadas: {conciliaciones_creadas}")

def crear_alertas_admin():
    print("Creando alertas administrativas...")
    
    try:
        usuario_admin = User.objects.get(username='admin')
        usuario_mlopez = User.objects.get(username='mlopez')
        
        tabla_pagos = TablaSistema.objects.get(nombre='Pagos')
        tabla_conciliaciones = TablaSistema.objects.get(nombre='Conciliaciones')
        
        # Crear alertas directamente (evita problemas de collation)
        alertas_data = [
            {
                'severidad': 'Critica',
                'tabla_sistema': tabla_pagos,
                'registro_afectado': 1,
                'mensaje': 'ALERTA: Diferencia critica detectada',
                'detalle': 'Pago con diferencia superior requiere atencion inmediata',
                'usuario_asignado': usuario_admin,
                'estado_gestion': False
            },
            {
                'severidad': 'Warning',
                'tabla_sistema': tabla_conciliaciones, 
                'registro_afectado': 1,
                'mensaje': 'ALERTA: Conciliacion con diferencias',
                'detalle': 'Diferencias pendientes en ultima conciliacion',
                'usuario_asignado': usuario_mlopez,
                'estado_gestion': False
            },
            {
                'severidad': 'Info',
                'tabla_sistema': tabla_pagos,
                'registro_afectado': 0,
                'mensaje': 'ALERTA: Pagos pendientes de validacion',
                'detalle': 'Pagos esperan validacion en el sistema',
                'usuario_asignado': usuario_mlopez,
                'estado_gestion': False
            }
        ]
        
        alertas_creadas = 0
        for alerta_data in alertas_data:
            try:
                AlertaAdmin.objects.create(**alerta_data)
                alertas_creadas += 1
                print(f"✅ Alerta creada: {alerta_data['mensaje']}")
            except Exception as e:
                print(f"❌ Error creando alerta: {e}")
        
        print(f"✅ Alertas admin creadas: {alertas_creadas}")
        
    except Exception as e:
        print(f"❌ Error en alertas admin: {e}")

def main():
    print("=== INICIANDO CREACIÓN DE DATOS DE PRUEBA COMPLETOS ===")
    print("📊 Creando datos limpios y sin errores...")
    
    try:
        # Limpiar datos existentes primero
        limpiar_datos_existentes()
        
        # Crear todos los datos
        crear_estados()
        crear_tablas_sistema()
        crear_tipos_accion()
        crear_usuarios()
        crear_pagos()
        crear_incidencias()
        crear_bitacora()
        crear_conciliaciones()
        crear_alertas_admin()
        
        print("\n" + "="*60)
        print("🎉 DATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print("="*60)
        print(f"📋 Estados: {Estado.objects.count()}")
        print(f"🗃️ Tablas Sistema: {TablaSistema.objects.count()}")
        print(f"⚡ Tipos Acción: {TipoAccion.objects.count()}")
        print(f"👥 Usuarios: {User.objects.count()}")
        print(f"💰 Pagos: {Pago.objects.count()}")
        print(f"⚠️ Incidencias: {Incidencia.objects.count()}")
        print(f"📝 Bitácora: {Bitacora.objects.count()}")
        print(f"🔄 Conciliaciones: {Conciliacion.objects.count()}")
        print(f"🚨 Alertas Admin: {AlertaAdmin.objects.count()}")
        print("\n¡Sistema completamente poblado para pruebas!")
        
    except Exception as e:
        print(f"❌ Error creando datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()