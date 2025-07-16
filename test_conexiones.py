#!/usr/bin/env python3
"""
Script de Prueba de Conexiones - Rexus.app
==========================================

Este script verifica que todas las conexiones a la base de datos
y funcionalidades implementadas funcionen correctamente.
"""

import sys
import os

# Agregar el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, date
from src.core.database import InventarioDatabaseConnection, UsersDatabaseConnection, AuditoriaDatabaseConnection

# Importar los modelos implementados
try:
    from src.modules.administracion.recursos_humanos.model import RecursosHumanosModel
    from src.modules.administracion.contabilidad.model import ContabilidadModel
    from src.modules.mantenimiento.model import MantenimientoModel
    from src.modules.logistica.model import LogisticaModel
    print("[OK] Todos los modulos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)


def test_database_connections():
    """Prueba las conexiones básicas a las bases de datos."""
    print("\n" + "="*60)
    print("🔍 PROBANDO CONEXIONES DE BASE DE DATOS")
    print("="*60)
    
    # Probar conexión a base de datos de inventario
    print("\n📊 Probando conexión a base de datos 'inventario'...")
    try:
        db_inventario = InventarioDatabaseConnection()
        if db_inventario._connection:
            print("✅ Conexión a 'inventario' exitosa")
            
            # Probar una consulta simple
            cursor = db_inventario.cursor()
            cursor.execute("SELECT COUNT(*) FROM sysobjects WHERE xtype='U'")
            tabla_count = cursor.fetchone()[0]
            print(f"✅ Número de tablas en 'inventario': {tabla_count}")
            cursor.close()
        else:
            print("❌ No se pudo conectar a 'inventario'")
            return False
    except Exception as e:
        print(f"❌ Error conectando a 'inventario': {e}")
        return False
    
    # Probar conexión a base de datos de usuarios
    print("\n👥 Probando conexión a base de datos 'users'...")
    try:
        db_users = UsersDatabaseConnection()
        if db_users._connection:
            print("✅ Conexión a 'users' exitosa")
            
            # Probar una consulta simple
            cursor = db_users.cursor()
            cursor.execute("SELECT COUNT(*) FROM sysobjects WHERE xtype='U'")
            tabla_count = cursor.fetchone()[0]
            print(f"✅ Número de tablas en 'users': {tabla_count}")
            cursor.close()
        else:
            print("❌ No se pudo conectar a 'users'")
    except Exception as e:
        print(f"❌ Error conectando a 'users': {e}")
    
    # Probar conexión a base de datos de auditoría
    print("\n📋 Probando conexión a base de datos 'auditoria'...")
    try:
        db_auditoria = AuditoriaDatabaseConnection()
        if db_auditoria._connection:
            print("✅ Conexión a 'auditoria' exitosa")
            
            # Probar una consulta simple
            cursor = db_auditoria.cursor()
            cursor.execute("SELECT COUNT(*) FROM sysobjects WHERE xtype='U'")
            tabla_count = cursor.fetchone()[0]
            print(f"✅ Número de tablas en 'auditoria': {tabla_count}")
            cursor.close()
        else:
            print("❌ No se pudo conectar a 'auditoria'")
    except Exception as e:
        print(f"❌ Error conectando a 'auditoria': {e}")
    
    return True


def test_recursos_humanos_model():
    """Prueba el modelo de Recursos Humanos."""
    print("\n" + "="*60)
    print("👥 PROBANDO MODELO DE RECURSOS HUMANOS")
    print("="*60)
    
    try:
        # Crear conexión y modelo
        db = InventarioDatabaseConnection()
        model = RecursosHumanosModel(db)
        
        print("✅ Modelo de Recursos Humanos inicializado correctamente")
        
        # Probar obtener empleados
        print("\n📋 Probando obtener empleados...")
        empleados = model.obtener_todos_empleados()
        print(f"✅ Empleados obtenidos: {len(empleados)} registros")
        
        # Probar estadísticas
        print("\n📊 Probando estadísticas de empleados...")
        estadisticas = model.obtener_estadisticas_empleados()
        print(f"✅ Estadísticas obtenidas: {len(estadisticas)} elementos")
        
        # Probar cálculo de nómina
        print("\n💰 Probando cálculo de nómina...")
        nomina = model.calcular_nomina(datetime.now().month, datetime.now().year)
        print(f"✅ Nómina calculada: {len(nomina)} empleados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en modelo de Recursos Humanos: {e}")
        return False


def test_contabilidad_model():
    """Prueba el modelo de Contabilidad."""
    print("\n" + "="*60)
    print("💰 PROBANDO MODELO DE CONTABILIDAD")
    print("="*60)
    
    try:
        # Crear conexión y modelo
        db = InventarioDatabaseConnection()
        model = ContabilidadModel(db)
        
        print("✅ Modelo de Contabilidad inicializado correctamente")
        
        # Probar obtener asientos contables
        print("\n📊 Probando obtener asientos contables...")
        asientos = model.obtener_asientos_contables()
        print(f"✅ Asientos contables obtenidos: {len(asientos)} registros")
        
        # Probar obtener recibos
        print("\n🧾 Probando obtener recibos...")
        recibos = model.obtener_recibos()
        print(f"✅ Recibos obtenidos: {len(recibos)} registros")
        
        # Probar estadísticas financieras
        print("\n📈 Probando estadísticas financieras...")
        estadisticas = model.obtener_estadisticas_financieras()
        print(f"✅ Estadísticas financieras obtenidas: {len(estadisticas)} elementos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en modelo de Contabilidad: {e}")
        return False


def test_mantenimiento_model():
    """Prueba el modelo de Mantenimiento."""
    print("\n" + "="*60)
    print("🔧 PROBANDO MODELO DE MANTENIMIENTO")
    print("="*60)
    
    try:
        # Crear conexión y modelo
        db = InventarioDatabaseConnection()
        model = MantenimientoModel(db)
        
        print("✅ Modelo de Mantenimiento inicializado correctamente")
        
        # Probar obtener equipos
        print("\n⚙️ Probando obtener equipos...")
        equipos = model.obtener_equipos()
        print(f"✅ Equipos obtenidos: {len(equipos)} registros")
        
        # Probar obtener herramientas
        print("\n🔨 Probando obtener herramientas...")
        herramientas = model.obtener_herramientas()
        print(f"✅ Herramientas obtenidas: {len(herramientas)} registros")
        
        # Probar obtener mantenimientos
        print("\n📅 Probando obtener mantenimientos...")
        mantenimientos = model.obtener_mantenimientos()
        print(f"✅ Mantenimientos obtenidos: {len(mantenimientos)} registros")
        
        # Probar estadísticas
        print("\n📊 Probando estadísticas de mantenimiento...")
        estadisticas = model.obtener_estadisticas_mantenimiento()
        print(f"✅ Estadísticas de mantenimiento obtenidas: {len(estadisticas)} elementos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en modelo de Mantenimiento: {e}")
        return False


def test_logistica_model():
    """Prueba el modelo de Logística."""
    print("\n" + "="*60)
    print("🚚 PROBANDO MODELO DE LOGÍSTICA")
    print("="*60)
    
    try:
        # Crear conexión y modelo
        db = InventarioDatabaseConnection()
        model = LogisticaModel(db)
        
        print("✅ Modelo de Logística inicializado correctamente")
        
        # Probar obtener transportes
        print("\n🚛 Probando obtener transportes...")
        transportes = model.obtener_transportes()
        print(f"✅ Transportes obtenidos: {len(transportes)} registros")
        
        # Probar obtener entregas
        print("\n📦 Probando obtener entregas...")
        entregas = model.obtener_entregas()
        print(f"✅ Entregas obtenidas: {len(entregas)} registros")
        
        # Probar obtener obras disponibles
        print("\n🏗️ Probando obtener obras disponibles...")
        obras = model.obtener_obras_disponibles()
        print(f"✅ Obras disponibles obtenidas: {len(obras)} registros")
        
        # Probar estadísticas
        print("\n📊 Probando estadísticas de logística...")
        estadisticas = model.obtener_estadisticas_logistica()
        print(f"✅ Estadísticas de logística obtenidas: {len(estadisticas)} elementos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en modelo de Logística: {e}")
        return False


def test_table_existence():
    """Verifica qué tablas existen en la base de datos."""
    print("\n" + "="*60)
    print("🗄️ VERIFICANDO EXISTENCIA DE TABLAS")
    print("="*60)
    
    try:
        db = InventarioDatabaseConnection()
        cursor = db.cursor()
        
        # Obtener todas las tablas de usuario
        cursor.execute("""
            SELECT name 
            FROM sysobjects 
            WHERE xtype='U' 
            ORDER BY name
        """)
        
        tablas = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📋 Tablas existentes en la base de datos 'inventario' ({len(tablas)}):")
        for tabla in tablas:
            print(f"   ✅ {tabla}")
        
        # Verificar tablas específicas que necesitamos
        tablas_requeridas = [
            'empleados', 'departamentos', 'asistencias', 'nomina', 'bonos_descuentos', 'historial_laboral',
            'libro_contable', 'recibos', 'pagos_obra', 'pagos_materiales',
            'equipos', 'herramientas', 'mantenimientos', 'programacion_mantenimiento',
            'transportes', 'entregas', 'detalle_entregas',
            'obras', 'inventario_perfiles'
        ]
        
        print(f"\n🔍 Verificando tablas requeridas por los módulos implementados:")
        tablas_faltantes = []
        
        for tabla in tablas_requeridas:
            if tabla in tablas:
                print(f"   ✅ {tabla} - EXISTE")
            else:
                print(f"   ❌ {tabla} - FALTANTE")
                tablas_faltantes.append(tabla)
        
        if tablas_faltantes:
            print(f"\n⚠️ ATENCIÓN: {len(tablas_faltantes)} tablas requeridas no existen:")
            for tabla in tablas_faltantes:
                print(f"   - {tabla}")
            print(f"\n💡 Consulta el archivo 'docs/TABLAS_ADICIONALES_REQUERIDAS.md' para crear estas tablas")
        else:
            print(f"\n🎉 ¡Todas las tablas requeridas existen!")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False


def main():
    """Función principal que ejecuta todas las pruebas."""
    print("🚀 INICIANDO PRUEBAS DE CONEXIÓN Y FUNCIONALIDAD - REXUS.APP")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    resultados = []
    
    # Ejecutar todas las pruebas
    pruebas = [
        ("Conexiones de Base de Datos", test_database_connections),
        ("Verificación de Tablas", test_table_existence),
        ("Modelo de Recursos Humanos", test_recursos_humanos_model),
        ("Modelo de Contabilidad", test_contabilidad_model),
        ("Modelo de Mantenimiento", test_mantenimiento_model),
        ("Modelo de Logística", test_logistica_model)
    ]
    
    for nombre_prueba, funcion_prueba in pruebas:
        try:
            resultado = funcion_prueba()
            resultados.append((nombre_prueba, resultado))
        except Exception as e:
            print(f"❌ Error crítico en {nombre_prueba}: {e}")
            resultados.append((nombre_prueba, False))
    
    # Mostrar resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*80)
    
    exitosas = 0
    fallidas = 0
    
    for nombre, resultado in resultados:
        if resultado:
            print(f"✅ {nombre}: EXITOSO")
            exitosas += 1
        else:
            print(f"❌ {nombre}: FALLIDO")
            fallidas += 1
    
    print(f"\n📈 ESTADÍSTICAS FINALES:")
    print(f"   ✅ Pruebas exitosas: {exitosas}")
    print(f"   ❌ Pruebas fallidas: {fallidas}")
    print(f"   📊 Total de pruebas: {len(resultados)}")
    print(f"   📈 Porcentaje de éxito: {(exitosas/len(resultados)*100):.1f}%")
    
    if fallidas == 0:
        print(f"\n🎉 ¡TODAS LAS PRUEBAS FUERON EXITOSAS!")
        print(f"✅ El sistema está listo para usar")
    else:
        print(f"\n⚠️ Se encontraron {fallidas} problemas que requieren atención")
        print(f"💡 Revisa los mensajes de error arriba para más detalles")
    
    print("="*80)


if __name__ == "__main__":
    main()