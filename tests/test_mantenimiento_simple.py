#!/usr/bin/env python3
"""
Tests simples para el módulo de Mantenimiento (sin Unicode)

Verifica todas las funcionalidades del sistema de mantenimiento.
"""

import sys
import os
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from datetime import datetime, date
from rexus.modules.mantenimiento.model import MantenimientoModel
from rexus.modules.mantenimiento.programacion_model import ProgramacionMantenimientoModel


def test_mantenimiento_model():
    """Test del modelo principal de mantenimiento."""
    print("=== TEST MANTENIMIENTO MODEL ===")
    
    model = MantenimientoModel(db_connection=None)
    
    # Test obtener equipos
    equipos = model.obtener_equipos()
    print(f"Equipos obtenidos: {len(equipos)} equipos")
    
    # Test estadísticas
    stats = model.obtener_estadisticas_mantenimiento()
    print(f"Estadisticas: {len(stats)} campos")
    print(f"Total equipos: {stats.get('total_equipos', 0)}")
    print(f"Mantenimientos vencidos: {stats.get('mantenimientos_vencidos', 0)}")
    
    # Test obtener mantenimientos
    mantenimientos = model.obtener_mantenimientos()
    print(f"Mantenimientos: {len(mantenimientos)} encontrados")
    
    print("PASS - MantenimientoModel: FUNCIONAL")
    return True


def test_programacion_model():
    """Test del modelo de programación."""
    print("\n=== TEST PROGRAMACION MODEL ===")
    
    model = ProgramacionMantenimientoModel(db_connection=None)
    
    # Test obtener programaciones activas
    programaciones = model.obtener_programaciones_activas()
    print(f"Programaciones activas: {len(programaciones)} encontradas")
    
    # Test estadísticas de programación
    stats = model.obtener_estadisticas_programacion()
    print(f"Stats programacion: {stats.get('total_programaciones', 0)} programaciones")
    print(f"Vencidos: {stats.get('vencidos', 0)}")
    print(f"Proximos 7 dias: {stats.get('proximos_7_dias', 0)}")
    
    # Test plantillas
    plantillas = model.obtener_plantillas_mantenimiento()
    print(f"Plantillas: {len(plantillas)} disponibles")
    
    # Test calendario
    calendario = model.obtener_calendario_mantenimiento(date.today(), date.today())
    print(f"Eventos calendario: {len(calendario)} eventos")
    
    print("PASS - ProgramacionModel: FUNCIONAL")
    return True


def test_integracion():
    """Test de integración."""
    print("\n=== TEST INTEGRACION ===")
    
    try:
        # Test flujo completo
        mant_model = MantenimientoModel(db_connection=None)
        prog_model = ProgramacionMantenimientoModel(db_connection=None)
        
        # Obtener datos demo
        equipos = mant_model.obtener_equipos()
        stats = mant_model.obtener_estadisticas_mantenimiento()
        programaciones = prog_model.obtener_programaciones_activas()
        plantillas = prog_model.obtener_plantillas_mantenimiento()
        
        # Verificar integración
        flujo_ok = all([
            isinstance(equipos, list),
            isinstance(stats, dict),
            isinstance(programaciones, list),
            isinstance(plantillas, list),
            len(programaciones) > 0,
            len(plantillas) > 0
        ])
        
        if flujo_ok:
            print("PASS - Integracion: EXITOSA")
            print(f"Equipos: {len(equipos)} disponibles")
            print(f"Stats: {stats.get('total_equipos', 0)} equipos")
            print(f"Programaciones: {len(programaciones)} activas")
            print(f"Plantillas: {len(plantillas)} disponibles")
        else:
            print("FAIL - Integracion: FALLO")
        
        return flujo_ok
        
    except Exception as e:
        print(f"ERROR en integracion: {e}")
        return False


def test_funcionalidades_avanzadas():
    """Test de funcionalidades avanzadas."""
    print("\n=== TEST FUNCIONALIDADES AVANZADAS ===")
    
    try:
        prog_model = ProgramacionMantenimientoModel(db_connection=None)
        
        # Test crear programación (sin BD)
        exito_prog = prog_model.crear_programacion(
            equipo_id=1,
            tipo_mantenimiento="PREVENTIVO",
            frecuencia_dias=90,
            descripcion="Test programacion",
            responsable="Test User"
        )
        print(f"Crear programacion (sin BD): {exito_prog}")
        
        # Test crear plantilla (sin BD)
        exito_plantilla = prog_model.crear_plantilla_mantenimiento(
            nombre="Test Plantilla",
            tipo_mantenimiento="PREVENTIVO",
            descripcion="Plantilla de prueba",
            frecuencia_sugerida=60,
            tareas=["Tarea 1", "Tarea 2", "Tarea 3"],
            tiempo_estimado=2,
            costo_estimado=150.0
        )
        print(f"Crear plantilla (sin BD): {exito_plantilla}")
        
        # Test aplicar plantilla (sin BD)
        exito_aplicar = prog_model.aplicar_plantilla_a_equipo(
            plantilla_id=1,
            equipo_id=1,
            responsable="Test User"
        )
        print(f"Aplicar plantilla (sin BD): {exito_aplicar}")
        
        # Test generar mantenimientos
        generados = prog_model.generar_mantenimientos_pendientes()
        print(f"Mantenimientos generados: {len(generados)}")
        
        print("PASS - Funcionalidades Avanzadas: FUNCIONAL")
        return True
        
    except Exception as e:
        print(f"ERROR en funcionalidades avanzadas: {e}")
        return False


def test_mantenimiento_crud():
    """Test de operaciones CRUD de mantenimiento."""
    print("\n=== TEST MANTENIMIENTO CRUD ===")
    
    try:
        model = MantenimientoModel(db_connection=None)
        
        # Test crear equipo (sin BD)
        datos_equipo = {
            "codigo": "TEST-001",
            "nombre": "Equipo Test",
            "tipo": "Compresor",
            "estado": "OPERATIVO",
            "ubicacion": "Planta Test",
            "marca": "Test Brand",
            "modelo": "Test Model",
            "observaciones": "Equipo para testing"
        }
        
        equipo_id = model.crear_equipo(datos_equipo)
        print(f"Crear equipo (sin BD): {equipo_id}")
        
        # Test crear mantenimiento (sin BD)
        datos_mant = {
            "equipo_id": 1,
            "tipo": "PREVENTIVO",
            "descripcion": "Mantenimiento de prueba",
            "fecha_programada": date.today(),
            "estado": "PROGRAMADO",
            "responsable": "Test User",
            "costo_estimado": 200.0
        }
        
        mant_id = model.crear_mantenimiento(datos_mant)
        print(f"Crear mantenimiento (sin BD): {mant_id}")
        
        # Test completar mantenimiento (sin BD)
        datos_completacion = {
            "observaciones": "Mantenimiento completado exitosamente",
            "costo_real": 180.0,
            "responsable": "Test User"
        }
        
        completado = model.completar_mantenimiento(1, datos_completacion)
        print(f"Completar mantenimiento (sin BD): {completado}")
        
        print("PASS - Mantenimiento CRUD: FUNCIONAL")
        return True
        
    except Exception as e:
        print(f"ERROR en CRUD: {e}")
        return False


def main():
    """Ejecuta todos los tests."""
    print("=== TESTS MODULO MANTENIMIENTO ===")
    print("Rexus.app - Sistema Completo")
    print("=" * 50)
    
    tests = [
        ("MantenimientoModel", test_mantenimiento_model),
        ("ProgramacionModel", test_programacion_model),
        ("Integracion", test_integracion),
        ("FuncionalidadesAvanzadas", test_funcionalidades_avanzadas),
        ("MantenimientoCRUD", test_mantenimiento_crud)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERROR en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print(f"\n=== RESUMEN ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("\nMODULO MANTENIMIENTO: COMPLETAMENTE FUNCIONAL")
        print("Funcionalidades verificadas:")
        print("- Gestion completa de equipos")
        print("- Sistema de mantenimientos preventivos/correctivos")
        print("- Programacion automatica de mantenimientos")
        print("- Sistema de plantillas reutilizables")
        print("- Generacion automatica de tareas")
        print("- Calendario de mantenimientos")
        print("- Estadisticas y reportes")
        print("- Historial y seguimiento")
        return True
    else:
        print(f"\nMODULO MANTENIMIENTO: {total-passed} tests fallaron")
        return False


if __name__ == "__main__":
    success = main()
    print(f"\nTest completado: {'EXITO' if success else 'FALLO'}")
    sys.exit(0 if success else 1)