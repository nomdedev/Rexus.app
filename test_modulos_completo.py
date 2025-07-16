#!/usr/bin/env python3
"""
Test completo de todos los módulos implementados
"""

import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_recursos_humanos():
    """Test del módulo de recursos humanos"""
    print("\n" + "="*60)
    print("TESTEANDO MODULO RECURSOS HUMANOS")
    print("="*60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        from src.modules.administracion.recursos_humanos.model import RecursosHumanosModel
        
        # Crear conexión y modelo
        db = InventarioDatabaseConnection()
        model = RecursosHumanosModel(db)
        
        # Test 1: Crear empleado
        print("\n[TEST 1] Creando empleado...")
        empleado_data = {
            'codigo': 'EMP001',
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'dni': '12345678',
            'telefono': '123-456-7890',
            'email': 'juan.perez@rexus.com',
            'fecha_ingreso': date.today(),
            'salario_base': 1500.00,
            'cargo': 'Supervisor',
            'departamento_id': 1
        }
        
        empleado_id = model.crear_empleado(empleado_data)
        if empleado_id:
            print(f"[OK] Empleado creado con ID: {empleado_id}")
        else:
            print("[ERROR] No se pudo crear el empleado")
        
        # Test 2: Obtener empleados
        print("\n[TEST 2] Obteniendo empleados...")
        empleados = model.obtener_todos_empleados()
        print(f"[OK] Se encontraron {len(empleados)} empleados")
        
        # Test 3: Registrar asistencia
        print("\n[TEST 3] Registrando asistencia...")
        if empleado_id:
            asistencia_data = {
                'empleado_id': empleado_id,
                'fecha': date.today(),
                'hora_entrada': '08:00',
                'hora_salida': '17:00',
                'horas_trabajadas': 8.0,
                'tipo': 'NORMAL'
            }
            
            asistencia_id = model.registrar_asistencia(asistencia_data)
            if asistencia_id:
                print(f"[OK] Asistencia registrada con ID: {asistencia_id}")
            else:
                print("[ERROR] No se pudo registrar la asistencia")
        
        # Test 4: Calcular nómina
        print("\n[TEST 4] Calculando nómina...")
        if empleado_id:
            nomina = model.calcular_nomina(empleado_id, 2024, 7)
            if nomina:
                print(f"[OK] Nómina calculada - Total: ${nomina.get('neto', 0):.2f}")
            else:
                print("[ERROR] No se pudo calcular la nómina")
        
        # Test 5: Obtener estadísticas
        print("\n[TEST 5] Obteniendo estadísticas...")
        stats = model.obtener_estadisticas_rh()
        print(f"[OK] Estadísticas obtenidas - Total empleados: {stats.get('total_empleados', 0)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en test de recursos humanos: {e}")
        return False

def test_contabilidad():
    """Test del módulo de contabilidad"""
    print("\n" + "="*60)
    print("TESTEANDO MODULO CONTABILIDAD")
    print("="*60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        from src.modules.administracion.contabilidad.model import ContabilidadModel
        
        # Crear conexión y modelo
        db = InventarioDatabaseConnection()
        model = ContabilidadModel(db)
        
        # Test 1: Crear asiento contable
        print("\n[TEST 1] Creando asiento contable...")
        asiento_data = {
            'fecha_asiento': date.today(),
            'tipo_asiento': 'INGRESO',
            'concepto': 'Pago de cliente',
            'referencia': 'FAC-001',
            'debe': 1000.00,
            'haber': 0.00,
            'usuario_creacion': 'TEST'
        }
        
        asiento_id = model.crear_asiento_contable(asiento_data)
        if asiento_id:
            print(f"[OK] Asiento creado con ID: {asiento_id}")
        else:
            print("[ERROR] No se pudo crear el asiento")
        
        # Test 2: Crear recibo
        print("\n[TEST 2] Creando recibo...")
        recibo_data = {
            'fecha_emision': date.today(),
            'tipo_recibo': 'INGRESO',
            'concepto': 'Pago de servicios',
            'beneficiario': 'Cliente Test',
            'monto': 500.00,
            'usuario_creacion': 'TEST'
        }
        
        recibo_id = model.crear_recibo(recibo_data)
        if recibo_id:
            print(f"[OK] Recibo creado con ID: {recibo_id}")
        else:
            print("[ERROR] No se pudo crear el recibo")
        
        # Test 3: Crear pago de material
        print("\n[TEST 3] Creando pago de material...")
        pago_data = {
            'producto': 'Cemento',
            'proveedor': 'Proveedor Test',
            'cantidad': 50.0,
            'precio_unitario': 25.00,
            'fecha_compra': date.today(),
            'usuario_creacion': 'TEST'
        }
        
        pago_id = model.crear_pago_material(pago_data)
        if pago_id:
            print(f"[OK] Pago de material creado con ID: {pago_id}")
        else:
            print("[ERROR] No se pudo crear el pago de material")
        
        # Test 4: Obtener estadísticas financieras
        print("\n[TEST 4] Obteniendo estadísticas financieras...")
        stats = model.obtener_estadisticas_financieras()
        print(f"[OK] Estadísticas obtenidas - Total recibos: {stats.get('recibos', {}).get('total_recibos', 0)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en test de contabilidad: {e}")
        return False

def test_mantenimiento():
    """Test del módulo de mantenimiento"""
    print("\n" + "="*60)
    print("TESTEANDO MODULO MANTENIMIENTO")
    print("="*60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        from src.modules.mantenimiento.model import MantenimientoModel
        
        # Crear conexión y modelo
        db = InventarioDatabaseConnection()
        model = MantenimientoModel(db)
        
        # Test 1: Crear equipo
        print("\n[TEST 1] Creando equipo...")
        equipo_data = {
            'codigo': 'EQ001',
            'nombre': 'Excavadora CAT',
            'tipo': 'MAQUINARIA',
            'modelo': 'CAT-320',
            'marca': 'Caterpillar',
            'numero_serie': 'SN123456',
            'fecha_adquisicion': date.today(),
            'ubicacion': 'Almacén Principal',
            'valor_adquisicion': 50000.00,
            'vida_util_anos': 10
        }
        
        equipo_id = model.crear_equipo(equipo_data)
        if equipo_id:
            print(f"[OK] Equipo creado con ID: {equipo_id}")
        else:
            print("[ERROR] No se pudo crear el equipo")
        
        # Test 2: Crear herramienta
        print("\n[TEST 2] Creando herramienta...")
        herramienta_data = {
            'codigo': 'HER001',
            'nombre': 'Martillo Neumático',
            'tipo': 'HERRAMIENTA',
            'marca': 'Bosch',
            'modelo': 'GBH-5000',
            'fecha_adquisicion': date.today(),
            'ubicacion': 'Taller',
            'valor_adquisicion': 500.00
        }
        
        herramienta_id = model.crear_herramienta(herramienta_data)
        if herramienta_id:
            print(f"[OK] Herramienta creada con ID: {herramienta_id}")
        else:
            print("[ERROR] No se pudo crear la herramienta")
        
        # Test 3: Crear mantenimiento
        print("\n[TEST 3] Creando mantenimiento...")
        if equipo_id:
            mantenimiento_data = {
                'equipo_id': equipo_id,
                'tipo': 'PREVENTIVO',
                'descripcion': 'Mantenimiento preventivo mensual',
                'fecha_programada': date.today(),
                'costo_estimado': 200.00,
                'responsable': 'Técnico Test'
            }
            
            mantenimiento_id = model.crear_mantenimiento(mantenimiento_data)
            if mantenimiento_id:
                print(f"[OK] Mantenimiento creado con ID: {mantenimiento_id}")
            else:
                print("[ERROR] No se pudo crear el mantenimiento")
        
        # Test 4: Obtener estadísticas
        print("\n[TEST 4] Obteniendo estadísticas...")
        stats = model.obtener_estadisticas_mantenimiento()
        print(f"[OK] Estadísticas obtenidas - Total equipos: {stats.get('total_equipos', 0)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en test de mantenimiento: {e}")
        return False

def test_logistica():
    """Test del módulo de logística"""
    print("\n" + "="*60)
    print("TESTEANDO MODULO LOGISTICA")
    print("="*60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        from src.modules.logistica.model import LogisticaModel
        
        # Crear conexión y modelo
        db = InventarioDatabaseConnection()
        model = LogisticaModel(db)
        
        # Test 1: Crear transporte
        print("\n[TEST 1] Creando transporte...")
        transporte_data = {
            'codigo': 'TR001',
            'tipo': 'CAMION',
            'proveedor': 'Transportes Test',
            'capacidad_kg': 5000.0,
            'capacidad_m3': 20.0,
            'costo_km': 2.50,
            'disponible': True
        }
        
        transporte_id = model.crear_transporte(transporte_data)
        if transporte_id:
            print(f"[OK] Transporte creado con ID: {transporte_id}")
        else:
            print("[ERROR] No se pudo crear el transporte")
        
        # Test 2: Obtener transportes
        print("\n[TEST 2] Obteniendo transportes...")
        transportes = model.obtener_transportes()
        print(f"[OK] Se encontraron {len(transportes)} transportes")
        
        # Test 3: Calcular costo de envío
        print("\n[TEST 3] Calculando costo de envío...")
        if transporte_id:
            costo = model.calcular_costo_envio(transporte_id, 100.0, 1000.0, 5.0)
            print(f"[OK] Costo calculado: ${costo:.2f}")
        
        # Test 4: Obtener estadísticas
        print("\n[TEST 4] Obteniendo estadísticas...")
        stats = model.obtener_estadisticas_logistica()
        print(f"[OK] Estadísticas obtenidas - Total transportes: {stats.get('total_transportes', 0)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en test de logística: {e}")
        return False

def main():
    """Ejecuta todos los tests"""
    print("INICIANDO TESTS COMPLETOS DE MODULOS")
    print("="*60)
    
    resultados = {}
    
    # Ejecutar tests
    resultados['recursos_humanos'] = test_recursos_humanos()
    resultados['contabilidad'] = test_contabilidad()
    resultados['mantenimiento'] = test_mantenimiento()
    resultados['logistica'] = test_logistica()
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("RESUMEN DE TESTS")
    print("="*60)
    
    exitosos = 0
    total = len(resultados)
    
    for modulo, exito in resultados.items():
        status = "[OK]" if exito else "[ERROR]"
        print(f"{status} {modulo.upper()}")
        if exito:
            exitosos += 1
    
    print(f"\nResultados finales:")
    print(f"  Módulos exitosos: {exitosos}")
    print(f"  Módulos con errores: {total - exitosos}")
    print(f"  Total módulos: {total}")
    print(f"  Porcentaje de éxito: {(exitosos/total*100):.1f}%")
    
    print("\n" + "="*60)
    print("TESTS COMPLETADOS")
    print("="*60)

if __name__ == "__main__":
    main()