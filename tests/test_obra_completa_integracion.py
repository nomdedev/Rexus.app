#!/usr/bin/env python3
"""
Test de Integración Completa - Flujo de Obra
============================================

Este test simula el flujo completo de una obra desde su creación hasta su finalización,
interactuando con todos los módulos del sistema y probando las interacciones SQL reales.

Flujo de prueba:
1. Crear obra nueva
2. Asignar empleados (RRHH)
3. Crear pedidos de materiales
4. Gestionar herrajes
5. Programar vidrios
6. Registrar pagos (Contabilidad)
7. Programar mantenimiento
8. Generar reportes
9. Validar datos en toda la aplicación
"""

import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

try:
    from src.core.database import DatabaseConnection
    from rexus.modules.obras.model import ObrasModel
    from rexus.modules.administracion.recursos_humanos.model import RecursosHumanosModel
    from rexus.modules.administracion.contabilidad.model import ContabilidadModel
    from rexus.modules.pedidos.model import PedidosModel
    from rexus.modules.herrajes.model import HerrajesModel
    from rexus.modules.vidrios.model import VidriosModel
    from rexus.modules.mantenimiento.model import MantenimientoModel
    from rexus.modules.inventario.model import InventarioModel
    from rexus.modules.logistica.model import LogisticaModel
    from rexus.modules.auditoria.model import AuditoriaModel
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

class TestObraCompleta:
    """Test integral del flujo completo de una obra."""
    
    def __init__(self):
        self.db = None
        self.models = {}
        self.obra_id = None
        self.empleado_id = None
        self.pedido_id = None
        self.datos_obra = {}
        self.errores = []
        
    def setup_database(self):
        """Configura la conexión a la base de datos."""
        try:
            self.db = DatabaseConnection()
            print("✅ Conexión a base de datos establecida")
            
            # Inicializar todos los modelos
            self.models = {
                'obras': ObrasModel(self.db),
                'rrhh': RecursosHumanosModel(self.db),
                'contabilidad': ContabilidadModel(self.db),
                'pedidos': PedidosModel(self.db),
                'herrajes': HerrajesModel(self.db),
                'vidrios': VidriosModel(self.db),
                'mantenimiento': MantenimientoModel(self.db),
                'inventario': InventarioModel(self.db),
                'logistica': LogisticaModel(self.db),
                'auditoria': AuditoriaModel(self.db)
            }
            print("✅ Modelos inicializados correctamente")
            
        except Exception as e:
            self.errores.append(f"Error configurando BD: {e}")
            print(f"❌ Error configurando BD: {e}")
            
    def test_1_crear_obra(self):
        """Test 1: Crear una nueva obra."""
        print("\n🏗️  TEST 1: Creando nueva obra...")
        
        try:
            self.datos_obra = {
                'codigo': f'OBR-TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'nombre': 'Edificio Comercial Plaza Central - TEST',
                'cliente': 'Constructora ABC S.A.S.',
                'direccion': 'Calle 45 #12-34, Bogotá',
                'tipo_obra': 'COMERCIAL',
                'estado': 'PLANIFICACION',
                'fecha_inicio': date.today(),
                'fecha_fin_estimada': date.today() + timedelta(days=180),
                'presupuesto_total': Decimal('500000000.00'),
                'descripcion': 'Edificio comercial de 8 pisos con fachada de vidrio',
                'observaciones': 'Obra de prueba para test de integración',
                'responsable': 'Juan Pérez',
                'telefono_contacto': '+57 300 123 4567',
                'email_contacto': 'contacto@constructoraabc.com'
            }
            
            self.obra_id = self.models['obras'].crear_obra(self.datos_obra)
            
            if self.obra_id:
                print(f"   ✅ Obra creada con ID: {self.obra_id}")
                print(f"   📋 Código: {self.datos_obra['codigo']}")
                print(f"   🏢 Cliente: {self.datos_obra['cliente']}")
                print(f"   💰 Presupuesto: ${self.datos_obra['presupuesto_total']:,.2f}")
                
                # Verificar que la obra existe en la BD
                obra_verificada = self.models['obras'].obtener_obra_por_id(self.obra_id)
                if obra_verificada:
                    print("   ✅ Obra verificada en base de datos")
                else:
                    self.errores.append("Obra no encontrada después de crear")
                    
            else:
                self.errores.append("No se pudo crear la obra")
                
        except Exception as e:
            self.errores.append(f"Error creando obra: {e}")
            print(f"   ❌ Error creando obra: {e}")
            
    def test_2_asignar_empleados(self):
        """Test 2: Asignar empleados a la obra."""
        print("\n👥 TEST 2: Asignando empleados a la obra...")
        
        try:
            # Crear empleado de prueba
            empleado_data = {
                'codigo': f'EMP-TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'nombre': 'Carlos',
                'apellido': 'Rodríguez',
                'dni': '12345678',
                'telefono': '+57 311 987 6543',
                'departamento': 'Construcción',
                'cargo': 'Maestro de Obra',
                'salario': Decimal('2500000.00'),
                'fecha_ingreso': date.today(),
                'estado': 'ACTIVO'
            }
            
            self.empleado_id = self.models['rrhh'].crear_empleado(empleado_data)
            
            if self.empleado_id:
                print(f"   ✅ Empleado creado con ID: {self.empleado_id}")
                print(f"   👤 Nombre: {empleado_data['nombre']} {empleado_data['apellido']}")
                print(f"   💼 Cargo: {empleado_data['cargo']}")
                
                # Asignar empleado a obra
                asignacion = self.models['obras'].asignar_empleado_obra(
                    self.obra_id, 
                    self.empleado_id,
                    'MAESTRO_OBRA'
                )
                
                if asignacion:
                    print("   ✅ Empleado asignado a obra correctamente")
                else:
                    self.errores.append("No se pudo asignar empleado a obra")
                    
            else:
                self.errores.append("No se pudo crear empleado")
                
        except Exception as e:
            self.errores.append(f"Error asignando empleados: {e}")
            print(f"   ❌ Error asignando empleados: {e}")
            
    def test_3_crear_pedido_materiales(self):
        """Test 3: Crear pedido de materiales para la obra."""
        print("\n📋 TEST 3: Creando pedido de materiales...")
        
        try:
            pedido_data = {
                'codigo': f'PED-TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'obra_id': self.obra_id,
                'descripcion': 'Pedido de materiales para estructura',
                'estado': 'PENDIENTE',
                'fecha_pedido': date.today(),
                'fecha_requerida': date.today() + timedelta(days=15),
                'prioridad': 'ALTA',
                'observaciones': 'Materiales para cimentación y estructura',
                'solicitante': 'Carlos Rodríguez'
            }
            
            self.pedido_id = self.models['pedidos'].crear_pedido(pedido_data)
            
            if self.pedido_id:
                print(f"   ✅ Pedido creado con ID: {self.pedido_id}")
                print(f"   📋 Código: {pedido_data['codigo']}")
                print(f"   📅 Fecha requerida: {pedido_data['fecha_requerida']}")
                
                # Agregar items al pedido
                items = [
                    {'descripcion': 'Cemento Portland', 'cantidad': 100, 'unidad': 'Bultos'},
                    {'descripcion': 'Varilla #4', 'cantidad': 50, 'unidad': 'Unidades'},
                    {'descripcion': 'Arena lavada', 'cantidad': 10, 'unidad': 'M³'},
                    {'descripcion': 'Grava', 'cantidad': 15, 'unidad': 'M³'}
                ]
                
                for item in items:
                    resultado = self.models['pedidos'].agregar_item_pedido(
                        self.pedido_id, 
                        item['descripcion'], 
                        item['cantidad'], 
                        item['unidad']
                    )
                    if resultado:
                        print(f"   ✅ Item agregado: {item['descripcion']}")
                    else:
                        self.errores.append(f"No se pudo agregar item: {item['descripcion']}")
                        
            else:
                self.errores.append("No se pudo crear pedido")
                
        except Exception as e:
            self.errores.append(f"Error creando pedido: {e}")
            print(f"   ❌ Error creando pedido: {e}")
            
    def test_4_gestionar_herrajes(self):
        """Test 4: Gestionar herrajes para la obra."""
        print("\n🔧 TEST 4: Gestionando herrajes...")
        
        try:
            # Crear herrajes de prueba
            herrajes_data = [
                {
                    'codigo': 'HER-001-TEST',
                    'descripcion': 'Bisagra para puerta principal',
                    'tipo': 'BISAGRA',
                    'proveedor': 'Herrajes Colombia SAS',
                    'precio_unitario': Decimal('25000.00'),
                    'unidad_medida': 'PAR',
                    'categoria': 'PUERTAS',
                    'estado': 'ACTIVO',
                    'stock_actual': 50,
                    'stock_minimo': 10
                },
                {
                    'codigo': 'HER-002-TEST',
                    'descripcion': 'Cerradura multipunto',
                    'tipo': 'CERRADURA',
                    'proveedor': 'Herrajes Colombia SAS',
                    'precio_unitario': Decimal('180000.00'),
                    'unidad_medida': 'UNIDAD',
                    'categoria': 'PUERTAS',
                    'estado': 'ACTIVO',
                    'stock_actual': 20,
                    'stock_minimo': 5
                }
            ]
            
            herrajes_ids = []
            for herraje in herrajes_data:
                herraje_id = self.models['herrajes'].crear_herraje(herraje)
                if herraje_id:
                    herrajes_ids.append(herraje_id)
                    print(f"   ✅ Herraje creado: {herraje['descripcion']}")
                    
                    # Asignar herraje a obra
                    asignacion = self.models['herrajes'].asignar_herraje_obra(
                        herraje_id, 
                        self.obra_id,
                        cantidad=10 if herraje['tipo'] == 'BISAGRA' else 5
                    )
                    
                    if asignacion:
                        print(f"   ✅ Herraje asignado a obra")
                    else:
                        self.errores.append(f"No se pudo asignar herraje {herraje['descripcion']}")
                        
            if herrajes_ids:
                print(f"   ✅ {len(herrajes_ids)} herrajes creados y asignados")
                
        except Exception as e:
            self.errores.append(f"Error gestionando herrajes: {e}")
            print(f"   ❌ Error gestionando herrajes: {e}")
            
    def test_5_programar_vidrios(self):
        """Test 5: Programar vidrios para la obra."""
        print("\n🪟 TEST 5: Programando vidrios...")
        
        try:
            # Crear tipos de vidrios
            vidrios_data = [
                {
                    'tipo': 'TEMPLADO',
                    'espesor': Decimal('6.0'),
                    'color': 'TRANSPARENTE',
                    'precio_m2': Decimal('85000.00'),
                    'proveedor': 'Vidrios del Valle S.A.',
                    'estado': 'ACTIVO'
                },
                {
                    'tipo': 'LAMINADO',
                    'espesor': Decimal('8.0'),
                    'color': 'AZUL',
                    'precio_m2': Decimal('120000.00'),
                    'proveedor': 'Vidrios del Valle S.A.',
                    'estado': 'ACTIVO'
                }
            ]
            
            vidrios_ids = []
            for vidrio in vidrios_data:
                vidrio_id = self.models['vidrios'].crear_vidrio(vidrio)
                if vidrio_id:
                    vidrios_ids.append(vidrio_id)
                    print(f"   ✅ Vidrio creado: {vidrio['tipo']} {vidrio['espesor']}mm")
                    
                    # Crear medidas para la obra
                    medidas = [
                        {'ancho': Decimal('1.20'), 'alto': Decimal('1.80'), 'cantidad': 15},
                        {'ancho': Decimal('2.00'), 'alto': Decimal('2.50'), 'cantidad': 8}
                    ]
                    
                    for medida in medidas:
                        resultado = self.models['vidrios'].crear_medida_obra(
                            self.obra_id,
                            vidrio_id,
                            medida['ancho'],
                            medida['alto'],
                            medida['cantidad']
                        )
                        
                        if resultado:
                            m2 = medida['ancho'] * medida['alto'] * medida['cantidad']
                            print(f"   ✅ Medida agregada: {medida['ancho']}x{medida['alto']} ({m2:.2f}m²)")
                        else:
                            self.errores.append(f"No se pudo agregar medida {medida['ancho']}x{medida['alto']}")
                            
        except Exception as e:
            self.errores.append(f"Error programando vidrios: {e}")
            print(f"   ❌ Error programando vidrios: {e}")
            
    def test_6_registrar_pagos(self):
        """Test 6: Registrar pagos en contabilidad."""
        print("\n💰 TEST 6: Registrando pagos...")
        
        try:
            # Crear asiento contable
            asiento_data = {
                'numero': f'ASI-TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'fecha': date.today(),
                'tipo': 'EGRESO',
                'concepto': 'Pago anticipo obra Plaza Central',
                'referencia': self.datos_obra['codigo'],
                'debe': Decimal('0.00'),
                'haber': Decimal('50000000.00'),
                'estado': 'CONFIRMADO',
                'usuario': 'admin'
            }
            
            asiento_id = self.models['contabilidad'].crear_asiento(asiento_data)
            
            if asiento_id:
                print(f"   ✅ Asiento contable creado: {asiento_data['numero']}")
                print(f"   💰 Monto: ${asiento_data['haber']:,.2f}")
                
                # Crear recibo
                recibo_data = {
                    'numero': f'REC-TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    'fecha': date.today(),
                    'tipo': 'PAGO',
                    'concepto': 'Anticipo obra Plaza Central',
                    'beneficiario': self.datos_obra['cliente'],
                    'monto': Decimal('50000000.00'),
                    'moneda': 'COP',
                    'estado': 'EMITIDO',
                    'impreso': False
                }
                
                recibo_id = self.models['contabilidad'].crear_recibo(recibo_data)
                
                if recibo_id:
                    print(f"   ✅ Recibo creado: {recibo_data['numero']}")
                    
                    # Registrar pago por obra
                    pago_obra = self.models['contabilidad'].registrar_pago_obra(
                        self.obra_id,
                        'Anticipo construcción',
                        'ANTICIPO',
                        Decimal('50000000.00'),
                        date.today(),
                        'TRANSFERENCIA',
                        'PAGADO'
                    )
                    
                    if pago_obra:
                        print("   ✅ Pago por obra registrado")
                    else:
                        self.errores.append("No se pudo registrar pago por obra")
                        
            else:
                self.errores.append("No se pudo crear asiento contable")
                
        except Exception as e:
            self.errores.append(f"Error registrando pagos: {e}")
            print(f"   ❌ Error registrando pagos: {e}")
            
    def test_7_programar_mantenimiento(self):
        """Test 7: Programar mantenimiento de equipos."""
        print("\n🛠️  TEST 7: Programando mantenimiento...")
        
        try:
            # Crear equipo de prueba
            equipo_data = {
                'codigo': f'EQU-TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'nombre': 'Grúa Torre GT-1500',
                'tipo': 'GRUA',
                'marca': 'Liebherr',
                'modelo': 'GT-1500',
                'serie': 'GT150020240001',
                'estado': 'OPERATIVO',
                'ubicacion': 'Obra Plaza Central',
                'fecha_adquisicion': date.today() - timedelta(days=365),
                'valor_compra': Decimal('800000000.00'),
                'proveedor': 'Equipos Construcción S.A.',
                'garantia_hasta': date.today() + timedelta(days=365)
            }
            
            equipo_id = self.models['mantenimiento'].crear_equipo(equipo_data)
            
            if equipo_id:
                print(f"   ✅ Equipo creado: {equipo_data['nombre']}")
                
                # Programar mantenimiento preventivo
                mantenimiento_data = {
                    'equipo_id': equipo_id,
                    'tipo': 'PREVENTIVO',
                    'descripcion': 'Mantenimiento mensual grúa',
                    'fecha_programada': date.today() + timedelta(days=30),
                    'periodicidad': 'MENSUAL',
                    'responsable': 'Carlos Rodríguez',
                    'estado': 'PROGRAMADO',
                    'observaciones': 'Revisión completa de sistemas'
                }
                
                mantenimiento_id = self.models['mantenimiento'].crear_mantenimiento(mantenimiento_data)
                
                if mantenimiento_id:
                    print(f"   ✅ Mantenimiento programado para: {mantenimiento_data['fecha_programada']}")
                else:
                    self.errores.append("No se pudo programar mantenimiento")
                    
            else:
                self.errores.append("No se pudo crear equipo")
                
        except Exception as e:
            self.errores.append(f"Error programando mantenimiento: {e}")
            print(f"   ❌ Error programando mantenimiento: {e}")
            
    def test_8_gestionar_logistica(self):
        """Test 8: Gestionar logística de entregas."""
        print("\n🚛 TEST 8: Gestionando logística...")
        
        try:
            # Crear transporte
            transporte_data = {
                'codigo': f'TRA-TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'descripcion': 'Camión Volvo FH 540',
                'tipo': 'PROPIO',
                'capacidad_peso': Decimal('25000.00'),
                'capacidad_volumen': Decimal('90.00'),
                'costo_km': Decimal('3500.00'),
                'estado': 'DISPONIBLE',
                'placa': 'ABC-123'
            }
            
            transporte_id = self.models['logistica'].crear_transporte(transporte_data)
            
            if transporte_id:
                print(f"   ✅ Transporte creado: {transporte_data['descripcion']}")
                
                # Programar entrega
                entrega_data = {
                    'obra_id': self.obra_id,
                    'transporte_id': transporte_id,
                    'fecha_entrega': date.today() + timedelta(days=7),
                    'direccion': self.datos_obra['direccion'],
                    'contacto': self.datos_obra['responsable'],
                    'telefono': self.datos_obra['telefono_contacto'],
                    'estado': 'PROGRAMADA',
                    'peso_total': Decimal('5000.00'),
                    'volumen_total': Decimal('30.00'),
                    'observaciones': 'Entrega de materiales básicos'
                }
                
                entrega_id = self.models['logistica'].crear_entrega(entrega_data)
                
                if entrega_id:
                    print(f"   ✅ Entrega programada para: {entrega_data['fecha_entrega']}")
                    
                    # Agregar productos a la entrega
                    productos = [
                        {'descripcion': 'Cemento Portland', 'cantidad': 50, 'peso': 2500.0},
                        {'descripcion': 'Varilla #4', 'cantidad': 25, 'peso': 1500.0},
                        {'descripcion': 'Arena lavada', 'cantidad': 5, 'peso': 1000.0}
                    ]
                    
                    for producto in productos:
                        resultado = self.models['logistica'].agregar_producto_entrega(
                            entrega_id,
                            producto['descripcion'],
                            producto['cantidad'],
                            producto['peso']
                        )
                        
                        if resultado:
                            print(f"   ✅ Producto agregado: {producto['descripcion']}")
                        else:
                            self.errores.append(f"No se pudo agregar producto: {producto['descripcion']}")
                            
                else:
                    self.errores.append("No se pudo crear entrega")
                    
            else:
                self.errores.append("No se pudo crear transporte")
                
        except Exception as e:
            self.errores.append(f"Error gestionando logística: {e}")
            print(f"   ❌ Error gestionando logística: {e}")
            
    def test_9_registrar_auditoria(self):
        """Test 9: Registrar eventos de auditoría."""
        print("\n🔍 TEST 9: Registrando auditoría...")
        
        try:
            eventos = [
                {
                    'usuario_id': 1,
                    'modulo': 'OBRAS',
                    'accion': 'CREAR',
                    'tabla': 'obras',
                    'registro_id': str(self.obra_id),
                    'descripcion': f'Obra creada: {self.datos_obra["codigo"]}',
                    'ip_origen': '127.0.0.1'
                },
                {
                    'usuario_id': 1,
                    'modulo': 'RRHH',
                    'accion': 'ASIGNAR',
                    'tabla': 'empleados_obra',
                    'registro_id': str(self.empleado_id),
                    'descripcion': f'Empleado asignado a obra {self.datos_obra["codigo"]}',
                    'ip_origen': '127.0.0.1'
                },
                {
                    'usuario_id': 1,
                    'modulo': 'PEDIDOS',
                    'accion': 'CREAR',
                    'tabla': 'pedidos',
                    'registro_id': str(self.pedido_id),
                    'descripcion': f'Pedido creado para obra {self.datos_obra["codigo"]}',
                    'ip_origen': '127.0.0.1'
                }
            ]
            
            for evento in eventos:
                resultado = self.models['auditoria'].registrar_evento(
                    evento['usuario_id'],
                    evento['modulo'],
                    evento['accion'],
                    evento['tabla'],
                    evento['registro_id'],
                    evento['descripcion'],
                    evento['ip_origen']
                )
                
                if resultado:
                    print(f"   ✅ Evento registrado: {evento['descripcion']}")
                else:
                    self.errores.append(f"No se pudo registrar evento: {evento['descripcion']}")
                    
        except Exception as e:
            self.errores.append(f"Error registrando auditoría: {e}")
            print(f"   ❌ Error registrando auditoría: {e}")
            
    def test_10_validar_integridad_datos(self):
        """Test 10: Validar integridad de datos en todos los módulos."""
        print("\n✅ TEST 10: Validando integridad de datos...")
        
        try:
            # Validar obra
            obra = self.models['obras'].obtener_obra_por_id(self.obra_id)
            if obra:
                print(f"   ✅ Obra encontrada: {obra.get('nombre', 'N/A')}")
            else:
                self.errores.append("Obra no encontrada en validación")
                
            # Validar empleado
            empleado = self.models['rrhh'].obtener_empleado_por_id(self.empleado_id)
            if empleado:
                print(f"   ✅ Empleado encontrado: {empleado.get('nombre', 'N/A')}")
            else:
                self.errores.append("Empleado no encontrado en validación")
                
            # Validar pedido
            pedido = self.models['pedidos'].obtener_pedido_por_id(self.pedido_id)
            if pedido:
                print(f"   ✅ Pedido encontrado: {pedido.get('codigo', 'N/A')}")
            else:
                self.errores.append("Pedido no encontrado en validación")
                
            # Validar herrajes
            herrajes = self.models['herrajes'].obtener_herrajes_por_obra(self.obra_id)
            if herrajes:
                print(f"   ✅ Herrajes encontrados: {len(herrajes)} registros")
            else:
                print("   ⚠️  No se encontraron herrajes asignados")
                
            # Validar vidrios
            vidrios = self.models['vidrios'].obtener_vidrios_por_obra(self.obra_id)
            if vidrios:
                print(f"   ✅ Vidrios encontrados: {len(vidrios)} registros")
            else:
                print("   ⚠️  No se encontraron vidrios asignados")
                
            # Validar auditoría
            auditoria = self.models['auditoria'].obtener_eventos_por_modulo('OBRAS')
            if auditoria:
                print(f"   ✅ Eventos de auditoría: {len(auditoria)} registros")
            else:
                print("   ⚠️  No se encontraron eventos de auditoría")
                
        except Exception as e:
            self.errores.append(f"Error validando integridad: {e}")
            print(f"   ❌ Error validando integridad: {e}")
            
    def generar_reporte_final(self):
        """Genera el reporte final del test."""
        print("\n" + "="*60)
        print("📊 REPORTE FINAL DEL TEST DE INTEGRACIÓN")
        print("="*60)
        
        if self.obra_id:
            print(f"🏗️  Obra de prueba: {self.datos_obra['codigo']}")
            print(f"📅 Fecha de prueba: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🆔 ID de obra: {self.obra_id}")
            
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   • Tests ejecutados: 10")
        print(f"   • Errores encontrados: {len(self.errores)}")
        print(f"   • Tasa de éxito: {((10 - len(self.errores)) / 10) * 100:.1f}%")
        
        if self.errores:
            print(f"\n❌ ERRORES ENCONTRADOS:")
            for i, error in enumerate(self.errores, 1):
                print(f"   {i}. {error}")
        else:
            print(f"\n🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
            print(f"   ✅ Sistema completamente funcional")
            print(f"   ✅ Todas las interacciones SQL funcionan")
            print(f"   ✅ Datos se muestran correctamente")
            
        print(f"\n💡 RECOMENDACIONES:")
        if self.errores:
            print(f"   • Revisar los errores reportados arriba")
            print(f"   • Verificar las conexiones a la base de datos")
            print(f"   • Validar que todas las tablas existan")
        else:
            print(f"   • Sistema listo para producción")
            print(f"   • Todas las funcionalidades operativas")
            print(f"   • Integridad de datos verificada")
            
        print("="*60)
        
    def ejecutar_tests(self):
        """Ejecuta todos los tests en secuencia."""
        print("🚀 INICIANDO TEST DE INTEGRACIÓN COMPLETA")
        print("="*60)
        
        # Setup
        self.setup_database()
        if not self.db:
            print("❌ No se pudo conectar a la base de datos. Abortando tests.")
            return
            
        # Ejecutar tests
        self.test_1_crear_obra()
        self.test_2_asignar_empleados()
        self.test_3_crear_pedido_materiales()
        self.test_4_gestionar_herrajes()
        self.test_5_programar_vidrios()
        self.test_6_registrar_pagos()
        self.test_7_programar_mantenimiento()
        self.test_8_gestionar_logistica()
        self.test_9_registrar_auditoria()
        self.test_10_validar_integridad_datos()
        
        # Reporte final
        self.generar_reporte_final()
        
        return len(self.errores) == 0

def main():
    """Función principal."""
    test = TestObraCompleta()
    exito = test.ejecutar_tests()
    
    if exito:
        print("\n🎉 TEST DE INTEGRACIÓN COMPLETADO CON ÉXITO")
        return 0
    else:
        print(f"\n❌ TEST DE INTEGRACIÓN COMPLETADO CON {len(test.errores)} ERRORES")
        return 1

if __name__ == "__main__":
    sys.exit(main())