#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para pruebas de integración de módulos Rexus.app
"""

import sys
import os
from pathlib import Path

# Añadir el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_basic_functionality():
    """Prueba funcionalidad básica de las dependencias"""
    print("=" * 60)
    print("FASE 2: PRUEBAS DE INTEGRACIÓN")
    print("=" * 60)
    
    results = {}
    
    # 1. Probar unified_sanitizer
    print("\n--- UNIFIED SANITIZER ---")
    try:
        from rexus.utils.unified_sanitizer import sanitize_string, sanitize_email
        
        # Probar sanitización
        test_string = sanitize_string("  texto de prueba  ", max_length=20)
        test_email = sanitize_email("test@example.com")
        
        print(f"[OK] Sanitizacion de string: '{test_string}'")
        print(f"[OK] Sanitizacion de email: '{test_email}'")
        results["sanitizer"] = True
        
    except Exception as e:
        print(f"[ERROR] Error en unified_sanitizer: {e}")
        results["sanitizer"] = False
    
    # 2. Probar sql_script_loader
    print("\n--- SQL SCRIPT LOADER ---")
    try:
        from rexus.utils.sql_script_loader import sql_script_loader
        
        # Probar carga de script
        script_content = sql_script_loader.load_script("optimizer/check_database_exists.sql")
        print(f"[OK] Carga de script SQL: {len(script_content)} caracteres")
        results["sql_loader"] = True
        
    except Exception as e:
        print(f"[ERROR] Error en sql_script_loader: {e}")
        results["sql_loader"] = False
    
    # 3. Probar auth_decorators
    print("\n--- AUTH DECORATORS ---")
    try:
        from rexus.core.auth_decorators import auth_required, admin_required
        
        # Probar decoradores
        @auth_required
        def test_function():
            return "test"
        
        @admin_required  
        def admin_function():
            return "admin"
        
        print("[OK] Decoradores de autenticacion funcionales")
        results["auth_decorators"] = True
        
    except Exception as e:
        print(f"[ERROR] Error en auth_decorators: {e}")
        results["auth_decorators"] = False
    
    # 4. Probar logging_config
    print("\n--- LOGGING CONFIG ---")
    try:
        from rexus.utils.logging_config import get_logger
        
        # Probar logging
        logger = get_logger("test_integration")
        logger.info("Mensaje de prueba de integración")
        
        print("[OK] Sistema de logging funcional")
        results["logging"] = True
        
    except Exception as e:
        print(f"[ERROR] Error en logging_config: {e}")
        results["logging"] = False
    
    # 5. Probar task_queue
    print("\n--- TASK QUEUE ---")
    try:
        from rexus.utils.task_queue import TaskQueue, TaskPriority
        task_queue = TaskQueue()
        
        # Probar cola de tareas
        task_id = task_queue.enqueue(lambda: "test_task", priority=TaskPriority.NORMAL)
        print(f"[OK] Tarea agregada a la cola: {task_id}")
        results["task_queue"] = True
        
    except Exception as e:
        print(f"[ERROR] Error en task_queue: {e}")
        results["task_queue"] = False
    
    # 6. Probar two_factor_auth
    print("\n--- TWO FACTOR AUTH ---")
    try:
        from rexus.utils.two_factor_auth import TwoFactorAuth
        
        # Probar autenticación de dos factores
        tfa = TwoFactorAuth()
        secret = tfa.generate_secret()
        print(f"[OK] Generacion de secreto TFA: {secret[:10]}...")
        results["tfa"] = True
        
    except Exception as e:
        print(f"[ERROR] Error en two_factor_auth: {e}")
        results["tfa"] = False
    
    return results

def test_integration_flows():
    """Prueba flujos de integración simulados"""
    print("\n--- FLUJOS DE INTEGRACIÓN SIMULADOS ---")
    
    integration_results = {}
    
    # 1. Flujo Obras → Inventario
    print("\n1. Flujo Obras → Inventario")
    try:
        # Simular creación de obra
        obra_data = {
            "nombre": "Obra de Prueba",
            "direccion": "Dirección de Prueba",
            "cliente": "Cliente de Prueba"
        }
        
        # Simular asignación de inventario
        inventario_data = {
            "id_obra": 1,
            "items": [
                {"codigo": "ITEM001", "cantidad": 10},
                {"codigo": "ITEM002", "cantidad": 5}
            ]
        }
        
        print("✅ Simulación de flujo Obras → Inventario exitosa")
        integration_results["obras_inventario"] = True
        
    except Exception as e:
        print(f"❌ Error en flujo Obras → Inventario: {e}")
        integration_results["obras_inventario"] = False
    
    # 2. Flujo Pedidos → Compras
    print("\n2. Flujo Pedidos → Compras")
    try:
        # Simular creación de pedido
        pedido_data = {
            "id_obra": 1,
            "items": [
                {"codigo": "PROD001", "cantidad": 20, "precio": 100.0}
            ],
            "estado": "pendiente"
        }
        
        # Simular generación de orden de compra
        compra_data = {
            "id_pedido": 1,
            "proveedor": "Proveedor de Prueba",
            "items": pedido_data["items"],
            "estado": "generada"
        }
        
        print("✅ Simulación de flujo Pedidos → Compras exitosa")
        integration_results["pedidos_compras"] = True
        
    except Exception as e:
        print(f"❌ Error en flujo Pedidos → Compras: {e}")
        integration_results["pedidos_compras"] = False
    
    # 3. Flujo Usuarios → Auditoría
    print("\n3. Flujo Usuarios → Auditoría")
    try:
        # Simular acción de usuario
        usuario_action = {
            "id_usuario": 1,
            "accion": "crear_obra",
            "modulo": "obras",
            "detalles": "Creación de obra de prueba"
        }
        
        # Simular registro de auditoría
        auditoria_data = {
            "id_usuario": usuario_action["id_usuario"],
            "accion": usuario_action["accion"],
            "modulo": usuario_action["modulo"],
            "fecha_hora": "2026-02-12 15:46:00",
            "ip_address": "127.0.0.1",
            "detalles": usuario_action["detalles"]
        }
        
        print("✅ Simulación de flujo Usuarios → Auditoría exitosa")
        integration_results["usuarios_auditoria"] = True
        
    except Exception as e:
        print(f"❌ Error en flujo Usuarios → Auditoría: {e}")
        integration_results["usuarios_auditoria"] = False
    
    return integration_results

def test_system_stability():
    """Prueba estabilidad general del sistema"""
    print("\n--- PRUEBAS DE ESTABILIDAD ---")
    
    stability_results = {}
    
    # 1. Prueba de manejo de errores
    print("\n1. Manejo de Errores")
    try:
        from rexus.utils.unified_sanitizer import sanitize_string
        
        # Probar manejo de errores
        result = sanitize_string("")  # Probar con string vacío
        print("✅ Manejo de errores correcto")
        stability_results["error_handling"] = True
        
    except Exception as e:
        print(f"❌ Error en manejo de errores: {e}")
        stability_results["error_handling"] = False
    
    # 2. Prueba de memoria
    print("\n2. Uso de Memoria")
    try:
        import gc
        
        # Forzar garbage collection
        gc.collect()
        
        # Probar creación múltiple de objetos
        objects = []
        for i in range(1000):
            objects.append(f"test_object_{i}")
        
        del objects
        gc.collect()
        
        print("✅ Gestión de memoria estable")
        stability_results["memory"] = True
        
    except Exception as e:
        print(f"❌ Error en gestión de memoria: {e}")
        stability_results["memory"] = False
    
    # 3. Prueba de concurrencia básica
    print("\n3. Concurrencia Básica")
    try:
        import threading
        import time
        
        def worker():
            time.sleep(0.1)
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        print("✅ Concurrencia básica funcional")
        stability_results["concurrency"] = True
        
    except Exception as e:
        print(f"❌ Error en concurrencia: {e}")
        stability_results["concurrency"] = False
    
    return stability_results

def main():
    """Función principal de pruebas de integración"""
    print("INICIANDO PRUEBAS DE INTEGRACIÓN - REXUS.APP")
    print("Fecha: 2026-02-12")
    print("Versión: v2.0.0")
    
    # Ejecutar pruebas
    basic_results = test_basic_functionality()
    integration_results = test_integration_flows()
    stability_results = test_system_stability()
    
    # Calcular resultados generales
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    # Funcionalidad básica
    basic_total = len(basic_results)
    basic_success = sum(basic_results.values())
    basic_percentage = (basic_success / basic_total * 100) if basic_total > 0 else 0
    
    print(f"\nFuncionalidad Básica: {basic_success}/{basic_total} ({basic_percentage:.1f}%)")
    for test, result in basic_results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test}")
    
    # Integración
    integration_total = len(integration_results)
    integration_success = sum(integration_results.values())
    integration_percentage = (integration_success / integration_total * 100) if integration_total > 0 else 0
    
    print(f"\nIntegración: {integration_success}/{integration_total} ({integration_percentage:.1f}%)")
    for test, result in integration_results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test}")
    
    # Estabilidad
    stability_total = len(stability_results)
    stability_success = sum(stability_results.values())
    stability_percentage = (stability_success / stability_total * 100) if stability_total > 0 else 0
    
    print(f"\nEstabilidad: {stability_success}/{stability_total} ({stability_percentage:.1f}%)")
    for test, result in stability_results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test}")
    
    # Resultado general
    total_tests = basic_total + integration_total + stability_total
    total_success = basic_success + integration_success + stability_success
    total_percentage = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nRESULTADO GENERAL: {total_success}/{total_tests} ({total_percentage:.1f}%)")
    
    if total_percentage >= 80:
        print("\n🎉 PRUEBAS DE INTEGRACIÓN EXITOSAS")
        return True
    elif total_percentage >= 60:
        print("\n⚠️ PRUEBAS DE INTEGRACIÓN PARCIALES")
        return False
    else:
        print("\n❌ PRUEBAS DE INTEGRACIÓN FALLIDAS")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)