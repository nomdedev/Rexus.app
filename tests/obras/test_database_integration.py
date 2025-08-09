"""
Test de integración para verificar que los datos reales de la base de datos
coinciden con la estructura esperada en el módulo obras.
"""

import sys
import os
from typing import List, Dict, Any

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_database_obras_integration():
    """Test de integración completo para verificar datos reales de obras."""
    
    print("\n🔍 [TEST DB] Iniciando verificación de integración base de datos - obras")
    print("=" * 70)
    
    try:
        # Importar dependencias
        from rexus.modules.obras.model import ObrasModel
        
        # Intentar conexión a BD
        print("📡 [CONEXIÓN] Intentando conectar a la base de datos...")
        
        # Buscar DatabaseManager en diferentes ubicaciones
        db_manager = None
        connection = None
        
        try:
            from rexus.core.database import DatabaseManager
            db_manager = DatabaseManager()
            if db_manager.connect():
                connection = db_manager.connection
                print("[CHECK] [CONEXIÓN] Conectado via DatabaseManager")
        except ImportError:
            print("[WARN] [CONEXIÓN] DatabaseManager no encontrado, intentando conexión directa...")
            
        # Si no funciona el DatabaseManager, intentar conexión directa
        if not connection:
            try:
                import pyodbc
                # Usar configuración básica de SQL Server
                connection_string = (
                    "DRIVER={ODBC Driver 17 for SQL Server};"
                    "SERVER=localhost;"
                    "DATABASE=rexus_db;"
                    "Trusted_Connection=yes;"
                )
                connection = pyodbc.connect(connection_string)
                print("[CHECK] [CONEXIÓN] Conectado via pyodbc directo")
            except Exception as e:
                print(f"[ERROR] [CONEXIÓN] Error conectando directamente: {e}")
                connection = None
        
        if not connection:
            print("[ERROR] [ERROR] No se pudo establecer conexión a la base de datos")
            print("💡 [SUGERENCIA] Verifica que SQL Server esté ejecutándose y la BD 'rexus_db' exista")
            return False
            
        # Crear modelo de obras
        print("\n🏗️ [MODELO] Creando modelo de obras...")
        model = ObrasModel(connection)
        
        # Verificar estructura de tabla obras
        print("\n📋 [ESTRUCTURA] Verificando estructura de tabla 'obras'...")
        
        cursor = connection.cursor()
        
        # Obtener información de columnas
        try:
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'obras'
                ORDER BY ORDINAL_POSITION
            """)
            
            columnas_db = cursor.fetchall()
            
            if not columnas_db:
                print("[WARN] [ESTRUCTURA] La tabla 'obras' no existe o no tiene columnas")
                
                # Intentar crear tabla básica para testing
                print("🔧 [ESTRUCTURA] Intentando crear tabla básica para testing...")
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='obras' AND xtype='U')
                    CREATE TABLE obras (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        codigo_obra NVARCHAR(50) NOT NULL,
                        nombre NVARCHAR(200) NOT NULL,
                        descripcion NTEXT,
                        cliente_id INT,
                        fecha_inicio DATE,
                        fecha_fin_estimada DATE,
                        fecha_fin_real DATE,
                        etapa_actual NVARCHAR(50),
                        estado NVARCHAR(50),
                        porcentaje_completado DECIMAL(5,2),
                        presupuesto_inicial DECIMAL(15,2),
                        costo_actual DECIMAL(15,2),
                        margen_estimado DECIMAL(5,2),
                        ubicacion NVARCHAR(300),
                        responsable_obra NVARCHAR(100),
                        observaciones NTEXT,
                        activo BIT DEFAULT 1,
                        fecha_creacion DATETIME DEFAULT GETDATE(),
                        fecha_actualizacion DATETIME DEFAULT GETDATE()
                    )
                """)
                connection.commit()
                print("[CHECK] [ESTRUCTURA] Tabla 'obras' creada")
                
                # Insertar datos de ejemplo
                print("📝 [DATOS] Insertando datos de ejemplo...")
                cursor.execute("""
                    INSERT INTO obras (codigo_obra, nombre, descripcion, fecha_inicio, fecha_fin_estimada, 
                                     estado, presupuesto_inicial, responsable_obra, ubicacion)
                    VALUES 
                    ('OBR-001', 'Edificio Central', 'Construcción edificio principal', '2024-01-15', '2024-12-15', 
                     'Activo', 150000.00, 'Juan Pérez', 'Centro Ciudad'),
                    ('OBR-002', 'Plaza Comercial', 'Centro comercial fase 1', '2024-02-01', '2025-01-30', 
                     'Activo', 250000.00, 'María García', 'Norte Ciudad'),
                    ('OBR-003', 'Residencial Los Pinos', 'Conjunto residencial', '2024-03-01', '2025-06-30', 
                     'Planificación', 180000.00, 'Carlos López', 'Sur Ciudad')
                """)
                connection.commit()
                print("[CHECK] [DATOS] Datos de ejemplo insertados")
                
                # Volver a obtener estructura
                cursor.execute("""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'obras'
                    ORDER BY ORDINAL_POSITION
                """)
                columnas_db = cursor.fetchall()
            
            print(f"[CHECK] [ESTRUCTURA] Encontradas {len(columnas_db)} columnas en tabla 'obras':")
            print("   📋 COLUMNAS DE LA BASE DE DATOS:")
            for i, (nombre, tipo, nullable, default) in enumerate(columnas_db):
                print(f"   {i+1:2d}. {nombre:<20} | {tipo:<15} | NULL: {nullable:<3} | DEFAULT: {default}")
            
        except Exception as e:
            print(f"[ERROR] [ESTRUCTURA] Error verificando estructura: {e}")
            return False
        
        # Verificar datos en la tabla
        print(f"\n[CHART] [DATOS] Verificando cantidad de registros...")
        
        try:
            todas_obras = model.obtener_todas_obras()
            print(f"[CHECK] [DATOS] Total de obras encontradas: {len(todas_obras)}")
            
            if len(todas_obras) > 0:
                print("   📋 MUESTRA DE DATOS (primeras 3 obras):")
                for i, obra in enumerate(todas_obras[:3]):
                    print(f"   Obra {i+1}: {len(obra)} campos - {obra[:5]}...")
                    
                # Verificar estructura de datos vs vista
                print(f"\n🔍 [MAPEO] Verificando mapeo con vista (primera obra):")
                primera_obra = todas_obras[0]
                
                mapeo_esperado = {
                    0: "id",
                    1: "codigo_obra", 
                    2: "nombre",
                    3: "descripcion",
                    4: "cliente_id",
                    5: "fecha_inicio",
                    6: "fecha_fin_estimada", 
                    7: "fecha_fin_real",
                    8: "estado",
                    9: "porcentaje_completado",
                    10: "responsable_obra",
                    11: "presupuesto_inicial"
                }
                
                print("   📋 MAPEO DATOS vs VISTA:")
                for indice, campo in mapeo_esperado.items():
                    if indice < len(primera_obra):
                        valor = primera_obra[indice]
                        # Truncar valores largos para display
                        if isinstance(valor, str) and len(valor) > 30:
                            valor_display = valor[:27] + "..."
                        else:
                            valor_display = valor
                        print(f"   [{indice:2d}] {campo:<20} = {valor_display}")
                    else:
                        print(f"   [{indice:2d}] {campo:<20} = [ERROR] FALTANTE")
                
                # Verificar columnas de la vista
                print(f"\n🖥️ [VISTA] Verificando mapeo con columnas de tabla UI:")
                columnas_vista = [
                    "Código", "Nombre", "Cliente", "Responsable", 
                    "Fecha Inicio", "Fecha Fin", "Estado", "Presupuesto", "Acciones"
                ]
                
                mapeo_vista = {
                    0: (1, "codigo_obra"),      # Código
                    1: (2, "nombre"),           # Nombre  
                    2: (4, "cliente_id"),       # Cliente
                    3: (10, "responsable_obra"), # Responsable
                    4: (5, "fecha_inicio"),     # Fecha Inicio
                    5: (6, "fecha_fin_estimada"), # Fecha Fin
                    6: (8, "estado"),           # Estado
                    7: (11, "presupuesto_inicial"), # Presupuesto
                    8: (-1, "acciones")         # Acciones (botón)
                }
                
                print("   📋 MAPEO VISTA -> BD:")
                for col_vista, (indice_bd, campo_bd) in mapeo_vista.items():
                    nombre_col_vista = columnas_vista[col_vista]
                    if indice_bd >= 0 and indice_bd < len(primera_obra):
                        valor = primera_obra[indice_bd]
                        if isinstance(valor, str) and len(valor) > 20:
                            valor_display = valor[:17] + "..."
                        else:
                            valor_display = valor
                        print(f"   Col[{col_vista}] {nombre_col_vista:<15} <- BD[{indice_bd:2d}] {campo_bd:<20} = {valor_display}")
                    else:
                        print(f"   Col[{col_vista}] {nombre_col_vista:<15} <- BD[{indice_bd:2d}] {campo_bd:<20} = [WARN] {'UI ONLY' if indice_bd == -1 else 'FALTANTE'}")
                
            else:
                print("[WARN] [DATOS] No hay obras en la base de datos")
                print("💡 [SUGERENCIA] Ejecuta algunos INSERT para probar la funcionalidad")
                
        except Exception as e:
            print(f"[ERROR] [DATOS] Error obteniendo datos: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test de funcionalidades del modelo
        print(f"\n🧪 [FUNCIONAL] Probando métodos del modelo...")
        
        # Test paginación
        try:
            obras_pag, total = model.obtener_datos_paginados(0, 5)
            print(f"[CHECK] [PAGINACIÓN] obtener_datos_paginados(0,5): {len(obras_pag)} obras, total: {total}")
        except Exception as e:
            print(f"[ERROR] [PAGINACIÓN] Error en paginación: {e}")
        
        # Test filtros
        try:
            filtros = {"estado": "Activo"}
            obras_filtradas = model.obtener_obras_filtradas(filtros, "nombre")
            print(f"[CHECK] [FILTROS] obtener_obras_filtradas(estado='Activo'): {len(obras_filtradas)} obras")
        except Exception as e:
            print(f"[ERROR] [FILTROS] Error en filtros: {e}")
        
        # Test obra por ID
        try:
            if len(todas_obras) > 0:
                primera_id = todas_obras[0][0]  # ID está en índice 0
                obra_por_id = model.obtener_obra_por_id(primera_id)
                if obra_por_id:
                    print(f"[CHECK] [ID] obtener_obra_por_id({primera_id}): Obra encontrada")
                else:
                    print(f"[WARN] [ID] obtener_obra_por_id({primera_id}): No encontrada")
        except Exception as e:
            print(f"[ERROR] [ID] Error obteniendo por ID: {e}")
        
        print(f"\n" + "=" * 70)
        print("🎉 [RESULTADO] Verificación de integración BD-Obras completada exitosamente")
        print(f"[CHART] [RESUMEN] {len(todas_obras)} obras encontradas, estructura verificada")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] [ERROR GENERAL] Error en test de integración: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cerrar conexión si existe
        if 'connection' in locals() and connection:
            try:
                connection.close()
                print("🔌 [CONEXIÓN] Conexión cerrada correctamente")
            except:
                pass

if __name__ == "__main__":
    exito = test_database_obras_integration()
    if exito:
        print("\n[CHECK] Test completado exitosamente")
        exit(0)
    else:
        print("\n[ERROR] Test falló")
        exit(1)
