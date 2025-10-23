# generar_datos_prueba.py
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from accounts.models import User
from validacion.models import (
    Estado, TablaSistema, TipoAccion, 
    Bitacora, Pago, Incidencia, Conciliacion
)

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
    
    acciones = [
        ('VALIDAR_PAGO', tabla_pagos),
        ('ANULAR_PAGO', tabla_pagos), 
        ('ALERTA_DIF', tabla_pagos),
        ('CREAR_PAGO', tabla_pagos),
        ('MODIFICAR_PAGO', tabla_pagos),
        ('CREAR_INCIDENCIA', tabla_incidencias),
        ('RESOLVER_INCIDENCIA', tabla_incidencias),
        ('CONCILIAR_PAGO', tabla_pagos),
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
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': nombre.split()[0],
                'last_name': nombre.split()[1] if len(nombre.split()) > 1 else '',
                'is_staff': is_staff,
                'is_active': True
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"👤 Usuario creado: {username}")
    print(f"✅ Usuarios creados: {User.objects.count()}")

def crear_pagos():
    print("Creando pagos de prueba...")
    usuario_admin = User.objects.get(username='admin')
    usuario_mlopez = User.objects.get(username='mlopez')
    
    # Valores de cuotas según tu información - MÁS ESTUDIANTES
    valores_cuotas = {
        'ENERO': 98000,
        'FEBRERO': 98000,
        'MARZO': 106000,
        'ABRIL': 106000, 
        'MAYO': 106000,
        'JUNIO': 106000,
        'JULIO': 106000,
        'AGOSTO': 106000,
        'SEPTIEMBRE': 106000,
        'OCTUBRE': 110000,
        'NOVIEMBRE': 110000,
        'DICIEMBRE': 110000,
    }
    
    # 10 ESTUDIANTES diferentes
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
                # Crear variaciones realistas en los montos
                monto_variado = monto
                if random.random() > 0.8:  # 20% de pagos con diferencias
                    monto_variado = monto - random.randint(1000, 5000)
                
                # Fechas realistas
                mes_numero = list(valores_cuotas.keys()).index(mes) + 1
                fecha_pago = timezone.now().replace(
                    year=2025, month=mes_numero, 
                    day=random.randint(1, 28), hour=12, minute=0, second=0, microsecond=0
                )
                
                fecha_vencimiento = timezone.now().replace(
                    year=2025, month=mes_numero, day=10, hour=0, minute=0, second=0, microsecond=0
                )
                
                # Estado variado
                estado = random.choices(
                    estados_pago, 
                    weights=[0.2, 0.6, 0.15, 0.05]  # Más validados, menos rechazados
                )[0]
                
                Pago.objects.get_or_create(
                    referencia=f"#P-{pago_id:05d}",
                    defaults={
                        'monto': monto_variado,
                        'fecha_pago': fecha_pago,
                        'fecha_vencimiento': fecha_vencimiento,
                        'estado': estado,
                        'estudiante_nombre': estudiante,
                        'concepto': f'Cuota {mes} 2025',
                        'metodo_pago': random.choice(metodos_pago),
                        'comision_porcentaje': random.choice([0, 1.5, 2.0, 3.0]),
                        'usuario_creacion': random.choice(usuarios_creacion),
                    }
                )
                pagos_creados += 1
                pago_id += 1
                
                # Crear algunos pagos duplicados/rechazados
                if random.random() > 0.95:  # 5% de pagos duplicados
                    Pago.objects.create(
                        referencia=f"#P-{pago_id:05d}",
                        monto=monto_variado,
                        fecha_pago=fecha_pago + timedelta(days=1),
                        fecha_vencimiento=fecha_vencimiento,
                        estado='RECHAZADO',
                        estudiante_nombre=estudiante,
                        concepto=f'Cuota {mes} 2025 - DUPLICADO',
                        metodo_pago=random.choice(metodos_pago),
                        comision_porcentaje=0,
                        usuario_creacion=random.choice(usuarios_creacion),
                    )
                    pago_id += 1
                    pagos_creados += 1
                
            except Exception as e:
                print(f"❌ Error creando pago {pago_id}: {e}")
                continue
    
    print(f"✅ Pagos creados: {pagos_creados}")

def crear_incidencias():
    print("Creando incidencias...")
    usuario_admin = User.objects.get(username='admin')
    usuario_mlopez = User.objects.get(username='mlopez')
    usuario_jdiaz = User.objects.get(username='jdiaz')
    
    # Obtener pagos para relacionar
    pagos = list(Pago.objects.all())
    
    tipos_incidencia = ['DIF_MONTO', 'SIN_MATCH', 'DUPLICADO', 'MONTO_ALTO', 'ANULACION', 'AJUSTE']
    estados_incidencia = ['ABIERTA', 'PENDIENTE_FIRMA', 'CERRADA']
    
    incidencias = [
        # Incidencias DIF_MONTO
        {
            'numero_referencia': 'DIF-001',
            'tipo_incidencia': 'DIF_MONTO',
            'estado': 'ABIERTA',
            'descripcion': 'Diferencia de $2.200 en pago #P-00121 - MacroClick',
            'monto_diferencia': 2200,
            'pago_relacionado': next((p for p in pagos if p.referencia == '#P-00121'), None),
            'usuario_asignado': usuario_mlopez
        },
        {
            'numero_referencia': 'DIF-002', 
            'tipo_incidencia': 'DIF_MONTO',
            'estado': 'PENDIENTE_FIRMA',
            'descripcion': 'Diferencia de $1.500 en pago #P-00135 - PagoFacil',
            'monto_diferencia': 1500,
            'pago_relacionado': next((p for p in pagos if p.referencia == '#P-00135'), None),
            'usuario_asignado': usuario_jdiaz
        },
        
        # Incidencias SIN_MATCH
        {
            'numero_referencia': 'SM-001',
            'tipo_incidencia': 'SIN_MATCH',
            'estado': 'ABIERTA', 
            'descripcion': 'Transferencia sin match - Ref: TRF-789456',
            'pago_relacionado': None,
            'usuario_asignado': usuario_mlopez
        },
        {
            'numero_referencia': 'SM-002',
            'tipo_incidencia': 'SIN_MATCH',
            'estado': 'ABIERTA',
            'descripcion': 'Pago #P-00142 no aparece en extracto bancario',
            'pago_relacionado': next((p for p in pagos if p.referencia == '#P-00142'), None),
            'usuario_asignado': usuario_jdiaz
        },
        
        # Incidencias DUPLICADO
        {
            'numero_referencia': 'DUP-001',
            'tipo_incidencia': 'DUPLICADO', 
            'estado': 'PENDIENTE_FIRMA',
            'descripcion': 'Pago duplicado #P-00150 - Estudiante: Ana Martinez',
            'pago_relacionado': next((p for p in pagos if p.referencia == '#P-00150'), None),
            'usuario_asignado': usuario_admin
        },
        
        # Incidencias ANULACION
        {
            'numero_referencia': 'ANU-001',
            'tipo_incidencia': 'ANULACION',
            'estado': 'PENDIENTE_FIRMA',
            'descripcion': 'Anulacion solicitada - Pago #P-00128',
            'pago_relacionado': next((p for p in pagos if p.referencia == '#P-00128'), None),
            'usuario_asignado': usuario_admin
        },
        
        # Incidencias MONTO_ALTO
        {
            'numero_referencia': 'MA-001',
            'tipo_incidencia': 'MONTO_ALTO',
            'estado': 'ABIERTA',
            'descripcion': 'Monto superior al esperado en pago #P-00180',
            'pago_relacionado': next((p for p in pagos if p.referencia == '#P-00180'), None),
            'usuario_asignado': usuario_mlopez
        }
    ]
    
    # Crear incidencias adicionales aleatorias
    for i in range(15):  # 15 incidencias más
        pago = random.choice(pagos) if pagos and random.random() > 0.3 else None
        incidencias.append({
            'numero_referencia': f'INC-{300 + i:03d}',
            'tipo_incidencia': random.choice(tipos_incidencia),
            'estado': random.choice(estados_incidencia),
            'descripcion': f'Incidencia automatica {i+1} - {random.choice(["MacroClick", "PagoFacil", "Transferencia"])}',
            'monto_diferencia': random.randint(500, 3000) if random.random() > 0.5 else None,
            'pago_relacionado': pago,
            'usuario_asignado': random.choice([usuario_admin, usuario_mlopez, usuario_jdiaz])
        })
    
    for incidencia_data in incidencias:
        try:
            Incidencia.objects.get_or_create(
                numero_referencia=incidencia_data['numero_referencia'],
                defaults=incidencia_data
            )
        except Exception as e:
            print(f"❌ Error creando incidencia {incidencia_data['numero_referencia']}: {e}")
    
    print(f"✅ Incidencias creadas: {Incidencia.objects.count()}")

def crear_bitacora():
    print("Creando bitácora...")
    tabla_pagos = TablaSistema.objects.get(nombre='Pagos')
    tabla_incidencias = TablaSistema.objects.get(nombre='Incidencias')
    
    usuario_admin = User.objects.get(username='admin')
    usuario_mlopez = User.objects.get(username='mlopez') 
    usuario_jdiaz = User.objects.get(username='jdiaz')
    usuario_sistema = User.objects.get(username='sistema')
    
    tipos_accion = {ta.nombre: ta for ta in TipoAccion.objects.all()}
    pagos = list(Pago.objects.all()[:20])  # Primeros 20 pagos
    incidencias = list(Incidencia.objects.all()[:10])  # Primeras 10 incidencias
    
    registros_bitacora = []
    
    # Registros de pagos
    for pago in pagos:
        registros_bitacora.extend([
            {
                'tipo_accion': tipos_accion['CREAR_PAGO'],
                'tabla_sistema': tabla_pagos,
                'observacion': f'Pago creado: {pago.referencia} - {pago.estudiante_nombre} - ${pago.monto}',
                'usuario': pago.usuario_creacion,
                'registro_afectado': pago.id,
                'valores_nuevos': {
                    'referencia': pago.referencia,
                    'monto': str(pago.monto),
                    'estudiante': pago.estudiante_nombre,
                    'estado': pago.estado
                },
                'fecha_base': pago.created_at  # Usar la fecha del pago como base
            }
        ])
        
        if pago.estado == 'VALIDADO':
            registros_bitacora.append({
                'tipo_accion': tipos_accion['VALIDAR_PAGO'],
                'tabla_sistema': tabla_pagos,
                'observacion': f'Pago validado: {pago.referencia}',
                'usuario': usuario_mlopez,
                'registro_afectado': pago.id,
                'valores_nuevos': {'estado': 'VALIDADO', 'usuario_validador': 'mlopez'},
                'fecha_base': pago.created_at + timedelta(hours=1)  # 1 hora después
            })
    
    # Registros de incidencias
    for incidencia in incidencias:
        registros_bitacora.append({
            'tipo_accion': tipos_accion['CREAR_INCIDENCIA'],
            'tabla_sistema': tabla_incidencias,
            'observacion': f'Incidencias creada: {incidencia.numero_referencia} - {incidencia.tipo_incidencia}',
            'usuario': usuario_sistema,
            'registro_afectado': incidencia.id,
            'valores_nuevos': {
                'numero_referencia': incidencia.numero_referencia,
                'tipo': incidencia.tipo_incidencia,
                'estado': incidencia.estado
            },
            'fecha_base': incidencia.fecha_apertura
        })
    
    # Registros de alertas del sistema
    alertas = [
        {
            'tipo_accion': tipos_accion['ALERTA_DIF'],
            'tabla_sistema': tabla_pagos,
            'observacion': 'ALERTA: Diferencia detectada en conciliacion MacroClick - $2.200',
            'usuario': usuario_sistema,
            'registro_afectado': 0,
            'valores_nuevos': {'alerta': 'DIF_MONTO', 'monto': '2200', 'origen': 'MacroClick'},
            'fecha_base': timezone.now() - timedelta(days=1, hours=2)
        },
        {
            'tipo_accion': tipos_accion['ALERTA_DIF'],
            'tabla_sistema': tabla_pagos,
            'observacion': 'ALERTA: Transferencia sin match - Ref: TRF-789456',
            'usuario': usuario_sistema,
            'registro_afectado': 0,
            'valores_nuevos': {'alerta': 'SIN_MATCH', 'referencia': 'TRF-789456'},
            'fecha_base': timezone.now() - timedelta(days=1, hours=1)
        }
    ]
    registros_bitacora.extend(alertas)
    
    # Crear registros en bitácora
    for bitacora_data in registros_bitacora:
        try:
            # ✅ CORRECCIÓN: Usar update() para establecer la fecha correcta
            bitacora = Bitacora.objects.create(
                tipo_accion=bitacora_data['tipo_accion'],
                tabla_sistema=bitacora_data['tabla_sistema'],
                observacion=bitacora_data['observacion'],
                usuario=bitacora_data['usuario'],
                registro_afectado=bitacora_data['registro_afectado'],
                valores_nuevos=bitacora_data['valores_nuevos'],
                estado=True
            )
            # ✅ Actualizar fecha usando update() para evitar que auto_now_add la sobreescriba
            Bitacora.objects.filter(id=bitacora.id).update(fecha=bitacora_data['fecha_base'])
            
        except Exception as e:
            print(f"❌ Error creando bitácora: {e}")
    
    print(f"✅ Registros bitácora creados: {Bitacora.objects.count()}")

def crear_conciliaciones():
    print("Creando conciliaciones...")
    usuario_admin = User.objects.get(username='admin')
    
    # Crear conciliaciones de los últimos 7 días
    for i in range(7):
        fecha = timezone.now().date() - timedelta(days=i)
        conciliacion, created = Conciliacion.objects.get_or_create(
            fecha_conciliacion=fecha,
            defaults={
                'pasarela': random.choice(['MacroClick', 'PagoFacil', 'Banco Nacion']),
                'estado': random.choice(['CONCILIADO', 'CON_DIFERENCIAS']),
                'usuario_responsable': usuario_admin,
                'match_sistema': random.randint(75, 95),
                'diferencias': random.randint(3, 15),
                'sin_match': random.randint(2, 10)
            }
        )
        if created:
            print(f"✅ Conciliación creada: {fecha}")
    
    print(f"✅ Conciliaciones creadas: {Conciliacion.objects.count()}")

def main():
    print("=== INICIANDO CREACIÓN DE DATOS DE PRUEBA MEJORADOS ===")
    print("📊 Creando datos más realistas y variados...")
    
    try:
        crear_estados()
        crear_tablas_sistema()
        crear_tipos_accion()
        crear_usuarios()
        crear_pagos()
        crear_incidencias()
        crear_bitacora()
        crear_conciliaciones()
        
        print("\n" + "="*50)
        print("🎉 DATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print("="*50)
        print(f"📋 Estados: {Estado.objects.count()}")
        print(f"🗃️ Tablas Sistema: {TablaSistema.objects.count()}")
        print(f"⚡ Tipos Acción: {TipoAccion.objects.count()}")
        print(f"👥 Usuarios: {User.objects.count()}")
        print(f"💰 Pagos: {Pago.objects.count()}")
        print(f"⚠️ Incidencias: {Incidencia.objects.count()}")
        print(f"📝 Bitácora: {Bitacora.objects.count()}")
        print(f"🔄 Conciliaciones: {Conciliacion.objects.count()}")
        print("\n¡Ahora puedes probar todas las funcionalidades!")
        
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()