#!/usr/bin/env python3
"""
Script de Prueba Simple - Rexus.app
===================================
Verifica conexiones y funcionalidades básicas
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Prueba las importaciones de módulos."""
    print("=" * 60)
    print("PROBANDO IMPORTACIONES DE MODULOS")
    print("=" * 60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        print("[OK] Importacion de database exitosa")
        
        from src.modules.administracion.recursos_humanos.model import RecursosHumanosModel
        print("[OK] Importacion de RecursosHumanosModel exitosa")
        
        from src.modules.administracion.contabilidad.model import ContabilidadModel
        print("[OK] Importacion de ContabilidadModel exitosa")
        
        from src.modules.mantenimiento.model import MantenimientoModel
        print("[OK] Importacion de MantenimientoModel exitosa")
        
        from src.modules.logistica.model import LogisticaModel
        print("[OK] Importacion de LogisticaModel exitosa")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Error importando modulos: {e}")
        return False

def test_database_connection():
    """Prueba la conexión básica a la base de datos."""
    print("\n" + "=" * 60)
    print("PROBANDO CONEXION A BASE DE DATOS")
    print("=" * 60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        db = InventarioDatabaseConnection()
        if db._connection:
            print("[OK] Conexion a base de datos 'inventario' exitosa")
            
            # Probar consulta simple
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) FROM sysobjects WHERE xtype='U'")
            count = cursor.fetchone()[0]
            print(f"[OK] Numero de tablas encontradas: {count}")
            cursor.close()
            
            return True
        else:
            print("[ERROR] No se pudo conectar a la base de datos")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error en conexion: {e}")
        return False

def test_table_existence():
    """Verifica qué tablas existen."""
    print("\n" + "=" * 60)
    print("VERIFICANDO EXISTENCIA DE TABLAS")
    print("=" * 60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        db = InventarioDatabaseConnection()
        cursor = db.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sysobjects WHERE xtype='U' ORDER BY name")
        tablas = [row[0] for row in cursor.fetchall()]
        
        print(f"\nTablas existentes ({len(tablas)}):")
        for tabla in tablas[:10]:  # Mostrar solo las primeras 10
            print(f"  - {tabla}")
        
        if len(tablas) > 10:
            print(f"  ... y {len(tablas) - 10} más")
        
        # Verificar tablas importantes
        tablas_importantes = ['obras', 'inventario_perfiles']
        print(f"\nVerificando tablas importantes:")
        for tabla in tablas_importantes:
            if tabla in tablas:
                print(f"  [OK] {tabla} existe")
            else:
                print(f"  [FALTA] {tabla} no existe")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error verificando tablas: {e}")
        return False

def test_basic_functionality():
    """Prueba funcionalidad básica de los modelos."""
    print("\n" + "=" * 60)
    print("PROBANDO FUNCIONALIDAD BASICA")
    print("=" * 60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        from src.modules.administracion.recursos_humanos.model import RecursosHumanosModel
        
        db = InventarioDatabaseConnection()
        model = RecursosHumanosModel(db)
        
        print("[OK] Modelo de Recursos Humanos inicializado")
        
        # Probar obtener empleados (debería funcionar aunque no haya datos)
        empleados = model.obtener_todos_empleados()
        print(f"[OK] Empleados obtenidos: {len(empleados)} registros")
        
        # Probar estadísticas
        estadisticas = model.obtener_estadisticas_empleados()
        print(f"[OK] Estadisticas obtenidas: {len(estadisticas)} elementos")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en funcionalidad basica: {e}")
        print(f"[INFO] Esto es normal si las tablas no existen aun")
        return False

def main():
    """Función principal."""
    print("INICIANDO PRUEBAS BASICAS - REXUS.APP")
    print("=" * 60)
    
    resultados = []
    
    # Ejecutar pruebas
    pruebas = [
        ("Importaciones", test_imports),
        ("Conexion BD", test_database_connection),
        ("Verificacion Tablas", test_table_existence),
        ("Funcionalidad Basica", test_basic_functionality)
    ]
    
    for nombre, funcion in pruebas:
        try:
            resultado = funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"[ERROR CRITICO] {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    exitosas = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        status = "[OK]" if resultado else "[FALLO]"
        print(f"{status} {nombre}")
    
    print(f"\nEstadisticas: {exitosas}/{total} pruebas exitosas")
    print(f"Porcentaje de exito: {(exitosas/total*100):.1f}%")
    
    if exitosas == total:
        print("\n[EXITO] Todas las pruebas fueron exitosas!")
    else:
        print(f"\n[ATENCION] {total - exitosas} pruebas fallaron")

if __name__ == "__main__":
    main()