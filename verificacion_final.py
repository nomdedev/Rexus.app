#!/usr/bin/env python3
"""
Verificación final del sistema completo
"""

import sys
import os
from datetime import datetime, date

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def verificar_tablas_base_datos():
    """Verifica que todas las tablas necesarias estén creadas"""
    print("\n" + "="*60)
    print("VERIFICANDO TABLAS DE BASE DE DATOS")
    print("="*60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        db = InventarioDatabaseConnection()
        cursor = db.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sysobjects WHERE xtype='U' ORDER BY name")
        tablas_existentes = [row[0] for row in cursor.fetchall()]
        
        # Tablas esperadas
        tablas_esperadas = [
            'empleados', 'departamentos', 'asistencias', 'nomina', 'bonos_descuentos', 'historial_laboral',
            'libro_contable', 'recibos', 'pagos_obra', 'pagos_materiales',
            'equipos', 'herramientas', 'mantenimientos', 'programacion_mantenimiento', 
            'tipos_mantenimiento', 'estado_equipos', 'historial_mantenimiento',
            'transportes', 'entregas', 'detalle_entregas', 'proveedores_transporte', 'rutas', 'costos_logisticos',
            'configuracion_sistema', 'parametros_modulos', 'auditoria_cambios', 'logs_sistema',
            'obras', 'productos', 'proveedores', 'usuarios'
        ]
        
        print(f"Total de tablas en la base de datos: {len(tablas_existentes)}")
        print("\nTablas encontradas:")
        for tabla in sorted(tablas_existentes):
            print(f"  - {tabla}")
        
        # Verificar tablas esperadas
        faltantes = []
        for tabla in tablas_esperadas:
            if tabla not in tablas_existentes:
                faltantes.append(tabla)
        
        if faltantes:
            print(f"\nTablas faltantes: {len(faltantes)}")
            for tabla in faltantes:
                print(f"  - {tabla}")
        else:
            print("\n[OK] Todas las tablas principales están creadas")
        
        cursor.close()
        return len(faltantes) == 0
        
    except Exception as e:
        print(f"[ERROR] Error verificando tablas: {e}")
        return False

def verificar_conexiones_modulos():
    """Verifica que todos los módulos se conecten correctamente"""
    print("\n" + "="*60)
    print("VERIFICANDO CONEXIONES DE MODULOS")
    print("="*60)
    
    modulos_exitosos = 0
    total_modulos = 0
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        # Test Recursos Humanos
        total_modulos += 1
        try:
            from src.modules.administracion.recursos_humanos.model import RecursosHumanosModel
            db = InventarioDatabaseConnection()
            model = RecursosHumanosModel(db)
            empleados = model.obtener_todos_empleados()
            print(f"[OK] Recursos Humanos - {len(empleados)} empleados")
            modulos_exitosos += 1
        except Exception as e:
            print(f"[ERROR] Recursos Humanos: {e}")
        
        # Test Contabilidad
        total_modulos += 1
        try:
            from src.modules.administracion.contabilidad.model import ContabilidadModel
            db = InventarioDatabaseConnection()
            model = ContabilidadModel(db)
            recibos = model.obtener_recibos()
            print(f"[OK] Contabilidad - {len(recibos)} recibos")
            modulos_exitosos += 1
        except Exception as e:
            print(f"[ERROR] Contabilidad: {e}")
        
        # Test Mantenimiento
        total_modulos += 1
        try:
            from src.modules.mantenimiento.model import MantenimientoModel
            db = InventarioDatabaseConnection()
            model = MantenimientoModel(db)
            equipos = model.obtener_equipos()
            print(f"[OK] Mantenimiento - {len(equipos)} equipos")
            modulos_exitosos += 1
        except Exception as e:
            print(f"[ERROR] Mantenimiento: {e}")
        
        # Test Logística
        total_modulos += 1
        try:
            from src.modules.logistica.model import LogisticaModel
            db = InventarioDatabaseConnection()
            model = LogisticaModel(db)
            transportes = model.obtener_transportes()
            print(f"[OK] Logística - {len(transportes)} transportes")
            modulos_exitosos += 1
        except Exception as e:
            print(f"[ERROR] Logística: {e}")
        
        # Test Obras
        total_modulos += 1
        try:
            from src.modules.obras.model import ObrasModel
            db = InventarioDatabaseConnection()
            model = ObrasModel(db)
            obras = model.obtener_obras()
            print(f"[OK] Obras - {len(obras)} obras")
            modulos_exitosos += 1
        except Exception as e:
            print(f"[ERROR] Obras: {e}")
        
        # Test Inventario
        total_modulos += 1
        try:
            from src.modules.inventario.model import InventarioModel
            db = InventarioDatabaseConnection()
            model = InventarioModel(db)
            productos = model.obtener_productos()
            print(f"[OK] Inventario - {len(productos)} productos")
            modulos_exitosos += 1
        except Exception as e:
            print(f"[ERROR] Inventario: {e}")
        
        print(f"\nResultado: {modulos_exitosos}/{total_modulos} módulos conectados exitosamente")
        return modulos_exitosos == total_modulos
        
    except Exception as e:
        print(f"[ERROR] Error verificando conexiones: {e}")
        return False

def verificar_datos_iniciales():
    """Verifica que los datos iniciales estén insertados"""
    print("\n" + "="*60)
    print("VERIFICANDO DATOS INICIALES")
    print("="*60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        db = InventarioDatabaseConnection()
        cursor = db.cursor()
        
        # Verificar departamentos
        cursor.execute("SELECT COUNT(*) FROM departamentos")
        count_departamentos = cursor.fetchone()[0]
        print(f"[OK] Departamentos: {count_departamentos}")
        
        # Verificar tipos de mantenimiento
        cursor.execute("SELECT COUNT(*) FROM tipos_mantenimiento")
        count_tipos = cursor.fetchone()[0]
        print(f"[OK] Tipos de mantenimiento: {count_tipos}")
        
        # Verificar configuración del sistema
        cursor.execute("SELECT COUNT(*) FROM configuracion_sistema")
        count_config = cursor.fetchone()[0]
        print(f"[OK] Configuraciones del sistema: {count_config}")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error verificando datos iniciales: {e}")
        return False

def generar_reporte_sistema():
    """Genera un reporte del estado del sistema"""
    print("\n" + "="*60)
    print("REPORTE DEL SISTEMA")
    print("="*60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        db = InventarioDatabaseConnection()
        cursor = db.cursor()
        
        # Estadísticas generales
        estadisticas = {}
        
        # Empleados
        cursor.execute("SELECT COUNT(*) FROM empleados WHERE activo = 1")
        estadisticas['empleados_activos'] = cursor.fetchone()[0]
        
        # Equipos
        cursor.execute("SELECT COUNT(*) FROM equipos WHERE activo = 1")
        estadisticas['equipos_activos'] = cursor.fetchone()[0]
        
        # Obras
        cursor.execute("SELECT COUNT(*) FROM obras WHERE activo = 1")
        estadisticas['obras_activas'] = cursor.fetchone()[0]
        
        # Productos
        cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
        estadisticas['productos_activos'] = cursor.fetchone()[0]
        
        # Transportes
        cursor.execute("SELECT COUNT(*) FROM transportes WHERE activo = 1")
        estadisticas['transportes_activos'] = cursor.fetchone()[0]
        
        # Asientos contables
        cursor.execute("SELECT COUNT(*) FROM libro_contable WHERE estado = 'ACTIVO'")
        estadisticas['asientos_contables'] = cursor.fetchone()[0]
        
        # Recibos
        cursor.execute("SELECT COUNT(*) FROM recibos WHERE estado = 'EMITIDO'")
        estadisticas['recibos_emitidos'] = cursor.fetchone()[0]
        
        print("Estadísticas del sistema:")
        for clave, valor in estadisticas.items():
            print(f"  {clave.replace('_', ' ').title()}: {valor}")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error generando reporte: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("VERIFICACION FINAL DEL SISTEMA REXUS.APP")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    resultados = {}
    
    # Ejecutar verificaciones
    resultados['tablas'] = verificar_tablas_base_datos()
    resultados['conexiones'] = verificar_conexiones_modulos()
    resultados['datos_iniciales'] = verificar_datos_iniciales()
    resultados['reporte'] = generar_reporte_sistema()
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    
    exitosos = sum(1 for resultado in resultados.values() if resultado)
    total = len(resultados)
    
    for verificacion, exito in resultados.items():
        status = "[OK]" if exito else "[ERROR]"
        print(f"{status} {verificacion.replace('_', ' ').title()}")
    
    print(f"\nResultados:")
    print(f"  Verificaciones exitosas: {exitosos}")
    print(f"  Verificaciones con errores: {total - exitosos}")
    print(f"  Total verificaciones: {total}")
    print(f"  Porcentaje de éxito: {(exitosos/total*100):.1f}%")
    
    if exitosos == total:
        print("\n🎉 [EXITO] El sistema está completamente funcional!")
    else:
        print("\n⚠️  [ATENCION] Algunas verificaciones fallaron")
    
    print("\n" + "="*60)
    print("VERIFICACION COMPLETADA")
    print("="*60)

if __name__ == "__main__":
    main()