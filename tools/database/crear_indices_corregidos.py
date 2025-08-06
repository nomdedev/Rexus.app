#!/usr/bin/env python3
"""
MIT License - Copyright (c) 2025 Rexus.app

Creador de Índices Corregidos - Rexus.app
========================================

Script para crear índices con los nombres de columna correctos basado
en la estructura real de las tablas verificada.
"""

import sys
from pathlib import Path
import datetime
from typing import Dict

# Agregar ruta del proyecto
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from rexus.core.database import get_users_connection, get_inventario_connection, get_auditoria_connection
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Módulos de base de datos no disponibles: {e}")
    DATABASE_AVAILABLE = False

class CorrectedIndexCreator:
    """Creador de índices con nombres de columna corregidos"""
    
    def __init__(self):
        self.results = {
            "created": [],
            "existing": [],
            "errors": []
        }
        
        # Índices corregidos basados en estructura real
        self.indices_corregidos = {
            "users": [
                {
                    "name": "idx_usuarios_usuario",
                    "table": "usuarios",
                    "columns": ["usuario"],
                    "reason": "Login y autenticación - consulta más frecuente",
                    "unique": True
                },
                {
                    "name": "idx_usuarios_email_unique",
                    "table": "usuarios", 
                    "columns": ["email"],
                    "reason": "Validación de unicidad de email",
                    "unique": True
                },
                {
                    "name": "idx_usuarios_estado_activo",
                    "table": "usuarios",
                    "columns": ["estado", "activo"],
                    "reason": "Filtrar usuarios activos por estado"
                },
                {
                    "name": "idx_usuarios_ultimo_acceso",
                    "table": "usuarios",
                    "columns": ["ultimo_acceso"],
                    "reason": "Reportes de actividad de usuarios"
                },
                {
                    "name": "idx_usuarios_bloqueo",
                    "table": "usuarios",
                    "columns": ["intentos_fallidos", "bloqueado_hasta"],
                    "reason": "Control de bloqueo por intentos fallidos"
                }
            ],
            "inventario": [
                # Tabla productos - ya se crearon correctamente
                {
                    "name": "idx_obras_codigo_unique",
                    "table": "obras",
                    "columns": ["codigo"],
                    "reason": "Búsqueda de obras por código",
                    "unique": True
                },
                {
                    "name": "idx_obras_cliente_responsable", 
                    "table": "obras",
                    "columns": ["cliente", "responsable"],
                    "reason": "Filtros por cliente y responsable"
                },
                {
                    "name": "idx_pedidos_fecha_estado",
                    "table": "pedidos",
                    "columns": ["fecha_pedido", "estado"],
                    "reason": "Listados de pedidos por fecha y estado"
                },
                {
                    "name": "idx_herrajes_categoria",
                    "table": "herrajes",
                    "columns": ["categoria"],
                    "reason": "Filtros por categoría de herrajes"
                },
                {
                    "name": "idx_herrajes_proveedor",
                    "table": "herrajes", 
                    "columns": ["proveedor"],
                    "reason": "Filtros por proveedor"
                },
                {
                    "name": "idx_vidrios_tipo_espesor",
                    "table": "vidrios",
                    "columns": ["tipo", "espesor"],
                    "reason": "Búsqueda por tipo y espesor de vidrio"
                },
                {
                    "name": "idx_vidrios_color",
                    "table": "vidrios",
                    "columns": ["color"],
                    "reason": "Filtros por color de vidrio"
                },
                {
                    "name": "idx_auditoria_inventario_fecha",
                    "table": "auditoria", 
                    "columns": ["fecha"],
                    "reason": "Consultas de auditoría por fecha en inventario"
                },
                {
                    "name": "idx_auditoria_inventario_usuario_accion",
                    "table": "auditoria",
                    "columns": ["usuario_id", "accion"],
                    "reason": "Trazabilidad de acciones por usuario en inventario"
                }
            ],
            "auditoria": [
                {
                    "name": "idx_auditoria_fecha",
                    "table": "auditoria",
                    "columns": ["fecha"],
                    "reason": "Consultas de auditoría por rango de fechas"
                },
                {
                    "name": "idx_auditoria_usuario_accion",
                    "table": "auditoria",
                    "columns": ["usuario_id", "accion"],
                    "reason": "Trazabilidad de acciones por usuario"
                },
                {
                    "name": "idx_auditoria_tabla",
                    "table": "auditoria",
                    "columns": ["tabla_afectada"],
                    "reason": "Filtros por tabla afectada en reportes"
                },
                {
                    "name": "idx_auditoria_estado",
                    "table": "auditoria",
                    "columns": ["estado"],
                    "reason": "Filtrar por estado de operación"
                }
            ]
        }
    
    def verificar_indice_existe(self, conexion, indice_nombre: str) -> bool:
        """Verifica si un índice ya existe"""
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM sys.indexes 
                WHERE name = ?
            """, (indice_nombre,))
            
            existe = cursor.fetchone()[0] > 0
            cursor.close()
            return existe
            
        except Exception as e:
            print(f"[ERROR] Error verificando índice {indice_nombre}: {e}")
            return False
    
    def crear_indice_corregido(self, conexion, indice_config: Dict) -> bool:
        """Crea un índice individual corregido"""
        
        nombre = indice_config["name"]
        tabla = indice_config["table"] 
        columnas = indice_config["columns"]
        es_unico = indice_config.get("unique", False)
        
        try:
            # Verificar si el índice ya existe
            if self.verificar_indice_existe(conexion, nombre):
                print(f"  [EXISTS] Índice '{nombre}' ya existe")
                self.results["existing"].append(nombre)
                return True
            
            # Construir statement CREATE INDEX
            columnas_str = ", ".join(f"[{col}]" for col in columnas)
            unique_keyword = "UNIQUE " if es_unico else ""
            
            create_sql = f"""
            CREATE {unique_keyword}NONCLUSTERED INDEX [{nombre}]
            ON [dbo].[{tabla}] ({columnas_str})
            WITH (ONLINE = OFF, FILLFACTOR = 90)
            """
            
            # Ejecutar creación del índice
            cursor = conexion.cursor()
            cursor.execute(create_sql)
            conexion.commit()
            cursor.close()
            
            print(f"  [CREATED] Índice '{nombre}' creado exitosamente")
            self.results["created"].append({
                "name": nombre,
                "table": tabla, 
                "columns": columnas,
                "unique": es_unico,
                "reason": indice_config.get("reason", "Optimización general")
            })
            
            return True
            
        except Exception as e:
            print(f"  [ERROR] Error creando índice '{nombre}': {e}")
            self.results["errors"].append(f"{nombre}: {str(e)}")
            return False
    
    def procesar_base_datos_corregida(self, db_name: str, get_connection_func):
        """Procesa una base de datos con índices corregidos"""
        
        print(f"\n{'='*60}")
        print(f"[CORRECTED INDEXES] Creando índices corregidos: {db_name.upper()}")
        print(f"{'='*60}")
        
        try:
            # Obtener conexión
            conexion = get_connection_func()
            if not conexion:
                print(f"[ERROR] No se pudo conectar a la base de datos {db_name}")
                return
            
            # Crear índices corregidos para esta base de datos
            indices_db = self.indices_corregidos.get(db_name, [])
            
            if not indices_db:
                print(f"[INFO] No hay índices corregidos definidos para {db_name}")
                conexion.close()
                return
            
            print(f"\n[INDEXES] Creando {len(indices_db)} índices corregidos para {db_name}")
            
            creados_exitosos = 0
            for indice_config in indices_db:
                print(f"\n[PROCESSING] {indice_config['name']} en tabla '{indice_config['table']}'")
                print(f"  Razón: {indice_config['reason']}")
                print(f"  Columnas: {', '.join(indice_config['columns'])}")
                
                if self.crear_indice_corregido(conexion, indice_config):
                    creados_exitosos += 1
            
            print(f"\n[SUMMARY] Base de datos {db_name}:")
            print(f"  Índices procesados: {len(indices_db)}")
            print(f"  Creados exitosamente: {creados_exitosos}")
            
            conexion.close()
            
        except Exception as e:
            print(f"[ERROR] Error procesando base de datos {db_name}: {e}")
    
    def ejecutar_creacion_corregida(self):
        """Ejecuta la creación de índices corregidos"""
        
        print("[CORRECTED INDEXES] Creando índices corregidos - Rexus.app")
        print("=" * 70)
        print(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not DATABASE_AVAILABLE:
            print("[ERROR] Módulos de base de datos no disponibles")
            return
        
        # Solo procesar las bases de datos que tienen índices pendientes
        databases = {
            "users": get_users_connection,
            "inventario": get_inventario_connection,
            "auditoria": get_auditoria_connection
        }
        
        # Procesar cada base de datos
        for db_name, connection_func in databases.items():
            self.procesar_base_datos_corregida(db_name, connection_func)
        
        # Mostrar resumen final
        self._mostrar_resumen_corregido()
    
    def _mostrar_resumen_corregido(self):
        """Muestra resumen final de índices corregidos"""
        
        print("\n" + "=" * 70)
        print("[FINAL REPORT] RESUMEN DE ÍNDICES CORREGIDOS")
        print("=" * 70)
        
        print(f"\n[STATISTICS] Estadísticas:")
        print(f"  Índices creados: {len(self.results['created'])}")
        print(f"  Índices ya existían: {len(self.results['existing'])}")
        print(f"  Errores: {len(self.results['errors'])}")
        
        if self.results['created']:
            print(f"\n[SUCCESS] ÍNDICES CREADOS:")
            for indice in self.results['created']:
                unique_str = " (UNIQUE)" if indice['unique'] else ""
                print(f"  + {indice['name']}{unique_str}")
                print(f"    Tabla: {indice['table']}")
                print(f"    Columnas: {', '.join(indice['columns'])}")
                print(f"    Propósito: {indice['reason']}")
                print()
        
        if self.results['existing']:
            print(f"\n[INFO] ÍNDICES EXISTENTES:")
            for indice in self.results['existing']:
                print(f"  = {indice}")
        
        if self.results['errors']:
            print(f"\n[ERRORS] ERRORES:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        total_procesados = len(self.results['created']) + len(self.results['existing'])
        print(f"\n[RESULT] CREACIÓN DE ÍNDICES COMPLETADA")
        print(f"  Total procesados: {total_procesados}")
        
        if len(self.results['errors']) == 0:
            print("[SUCCESS] Todos los índices corregidos fueron creados exitosamente")
        else:
            print("[WARNING] Algunos índices tuvieron errores")

def main():
    """Función principal"""
    
    try:
        # Crear y ejecutar creador de índices corregidos
        creator = CorrectedIndexCreator()
        creator.ejecutar_creacion_corregida()
        
        print(f"\n[INFO] Proceso completado.")
        
    except Exception as e:
        print(f"[ERROR] Error ejecutando creación de índices: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()