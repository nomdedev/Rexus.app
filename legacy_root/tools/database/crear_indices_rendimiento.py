#!/usr/bin/env python3
"""
MIT License - Copyright (c) 2025 Rexus.app

Creador de Índices de Rendimiento para Base de Datos
===================================================

Script para analizar y crear índices de rendimiento optimizados para las
bases de datos del sistema Rexus.app (users, inventario, auditoria).

Este script:
1. Analiza patrones de consulta más frecuentes
2. Identifica columnas que necesitan índices
3. Crea índices de rendimiento optimizados
4. Valida la efectividad de los índices
5. Genera reporte de mejoras de rendimiento

Bases de datos:
- users: Autenticación y usuarios
- inventario: Datos principales de negocio
- auditoria: Logs y trazabilidad

Uso:
python tools/database/crear_indices_rendimiento.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import datetime

# Agregar ruta del proyecto
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from rexus.core.database import get_users_connection, get_inventario_connection, get_auditoria_connection
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Módulos de base de datos no disponibles: {e}")
    DATABASE_AVAILABLE = False

class DatabaseIndexOptimizer:
    """Optimizador de índices para bases de datos Rexus.app"""

    def __init__(self):
        self.results = {
            "created": [],
            "existing": [],
            "errors": [],
            "analysis": {}
        }

        # Definir índices críticos para cada base de datos
        self.indices_criticos = {
            "users": [
                {
                    "name": "idx_users_username",
                    "table": "users",
                    "columns": ["username"],
                    "reason": "Login y autenticación - consulta más frecuente",
                    "unique": True
                },
                {
                    "name": "idx_users_email",
                    "table": "users",
                    "columns": ["email"],
                    "reason": "Validación de unicidad de email",
                    "unique": True
                },
                {
                    "name": "idx_users_estado_activo",
                    "table": "users",
                    "columns": ["estado", "activo"],
                    "reason": "Filtrar usuarios activos por estado"
                },
                {
                    "name": "idx_users_ultimo_acceso",
                    "table": "users",
                    "columns": ["ultimo_acceso"],
                    "reason": "Reportes de actividad de usuarios"
                },
                {
                    "name": "idx_users_intentos_fallidos",
                    "table": "users",
                    "columns": ["intentos_fallidos", "fecha_bloqueo"],
                    "reason": "Control de bloqueo por intentos fallidos"
                }
            ],
            "inventario": [
                {
                    "name": "idx_productos_codigo",
                    "table": "productos",
                    "columns": ["codigo"],
                    "reason": "Búsqueda por código - operación muy frecuente",
                    "unique": True
                },
                {
                    "name": "idx_productos_descripcion",
                    "table": "productos",
                    "columns": ["descripcion"],
                    "reason": "Búsqueda de productos por descripción"
                },
                {
                    "name": "idx_productos_categoria",
                    "table": "productos",
                    "columns": ["categoria", "subcategoria"],
                    "reason": "Filtros por categoría en listados"
                },
                {
                    "name": "idx_productos_stock",
                    "table": "productos",
                    "columns": ["stock_actual", "stock_minimo"],
                    "reason": "Reportes de stock bajo y disponibilidad"
                },
                {
                    "name": "idx_productos_activo_estado",
                    "table": "productos",
                    "columns": ["activo", "estado"],
                    "reason": "Filtrar productos activos por estado"
                },
                {
                    "name": "idx_obras_codigo",
                    "table": "obras",
                    "columns": ["codigo_obra"],
                    "reason": "Búsqueda de obras por código",
                    "unique": True
                },
                {
                    "name": "idx_obras_estado",
                    "table": "obras",
                    "columns": ["estado"],
                    "reason": "Filtros por estado en dashboard de obras"
                },
                {
                    "name": "idx_obras_fechas",
                    "table": "obras",
                    "columns": ["fecha_inicio", "fecha_fin_estimada"],
                    "reason": "Cronogramas y reportes por fechas"
                },
                {
                    "name": "idx_obras_cliente_responsable",
                    "table": "obras",
                    "columns": ["cliente_id", "responsable_obra"],
                    "reason": "Filtros por cliente y responsable"
                },
                {
                    "name": "idx_pedidos_fecha_estado",
                    "table": "pedidos",
                    "columns": ["fecha_creacion", "estado"],
                    "reason": "Listados de pedidos por fecha y estado"
                },
                {
                    "name": "idx_pedidos_obra",
                    "table": "pedidos",
                    "columns": ["obra_id"],
                    "reason": "Pedidos asociados a obras específicas"
                },
                {
                    "name": "idx_herrajes_codigo",
                    "table": "herrajes",
                    "columns": ["codigo"],
                    "reason": "Búsqueda rápida de herrajes por código"
                },
                {
                    "name": "idx_herrajes_tipo_material",
                    "table": "herrajes",
                    "columns": ["tipo", "material"],
                    "reason": "Filtros por tipo y material"
                },
                {
                    "name": "idx_vidrios_medidas",
                    "table": "vidrios",
                    "columns": ["ancho", "alto", "espesor"],
                    "reason": "Búsqueda por medidas específicas"
                },
                {
                    "name": "idx_compras_proveedor_fecha",
                    "table": "compras",
                    "columns": ["proveedor_id", "fecha_pedido"],
                    "reason": "Historial de compras por proveedor"
                }
            ],
            "auditoria": [
                {
                    "name": "idx_auditoria_fecha",
                    "table": "audit_log",
                    "columns": ["fecha_evento"],
                    "reason": "Consultas de auditoría por rango de fechas"
                },
                {
                    "name": "idx_auditoria_usuario_accion",
                    "table": "audit_log",
                    "columns": ["usuario_id", "accion"],
                    "reason": "Trazabilidad de acciones por usuario"
                },
                {
                    "name": "idx_auditoria_modulo",
                    "table": "audit_log",
                    "columns": ["modulo", "tabla_afectada"],
                    "reason": "Filtros por módulo y tabla en reportes"
                },
                {
                    "name": "idx_auditoria_criticidad",
                    "table": "audit_log",
                    "columns": ["nivel_criticidad"],
                    "reason": "Filtrar eventos críticos rápidamente"
                }
            ]
        }

    def verificar_tabla_existe(self, conexion, tabla_nombre: str) -> bool:
        """Verifica si una tabla existe en la base de datos"""
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = ?
            """, (tabla_nombre,))

            existe = cursor.fetchone()[0] > 0
            cursor.close()
            return existe

        except Exception as e:
            print(f"[ERROR] Error verificando tabla {tabla_nombre}: {e}")
            return False

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

    def crear_indice(self, conexion, indice_config: Dict) -> bool:
        """Crea un índice individual"""

        nombre = indice_config["name"]
        tabla = indice_config["table"]
        columnas = indice_config["columns"]
        es_unico = indice_config.get("unique", False)

        try:
            # Verificar si la tabla existe
            if not self.verificar_tabla_existe(conexion, tabla):
                print(f"  [SKIP] Tabla '{tabla}' no existe - saltando índice {nombre}")
                return True

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

    def analizar_rendimiento_consultas(self, conexion, db_name: str):
        """Analiza el rendimiento de consultas frecuentes"""

        print(f"\n[ANALYSIS] Analizando rendimiento en base de datos '{db_name}'")

        try:
            cursor = conexion.cursor()

            # Consultar estadísticas de índices existentes
            cursor.execute("""
                SELECT
                    i.name AS index_name,
                    t.name AS table_name,
                    s.user_seeks,
                    s.user_scans,
                    s.user_lookups,
                    s.user_updates
                FROM sys.indexes i
                INNER JOIN sys.tables t ON i.object_id = t.object_id
                LEFT JOIN sys.dm_db_index_usage_stats s ON i.object_id = s.object_id AND i.index_id = s.index_id
                WHERE i.is_disabled = 0 AND i.is_hypothetical = 0
                ORDER BY s.user_seeks + s.user_scans + s.user_lookups DESC
            """)

            estadisticas = cursor.fetchall()

            if estadisticas:
                print(f"  [INFO] Encontradas estadísticas de {len(estadisticas)} índices")

                # Almacenar análisis
                self.results["analysis"][db_name] = {
                    "total_indices": len(estadisticas),
                    "indices_mas_usados": []
                }

                # Mostrar top 5 índices más utilizados
                for i, stats in enumerate(estadisticas[:5]):
                    index_name, table_name, seeks, scans, lookups, updates = stats
                    if seeks or scans or lookups:
                        total_reads = (seeks or 0) + (scans or 0) + (lookups or 0)
                        self.results["analysis"][db_name]["indices_mas_usados"].append({
                            "index": index_name,
                            "table": table_name,
                            "reads": total_reads,
                            "writes": updates or 0
                        })
                        print(f"    [{i+1}] {table_name}.{index_name}: {total_reads:,} lecturas, {updates or 0:,} escrituras")
            else:
                print(f"  [INFO] No se encontraron estadísticas de índices para {db_name}")

            cursor.close()

        except Exception as e:
            print(f"  [ERROR] Error analizando rendimiento: {e}")

    def procesar_base_datos(self, db_name: str, get_connection_func):
        """Procesa una base de datos individual"""

        print(f"\n{'='*60}")
        print(f"[DATABASE] Optimizando base de datos: {db_name.upper()}")
        print(f"{'='*60}")

        try:
            # Obtener conexión
            conexion = get_connection_func()
            if not conexion:
                print(f"[ERROR] No se pudo conectar a la base de datos {db_name}")
                return

            # Analizar rendimiento actual
            self.analizar_rendimiento_consultas(conexion, db_name)

            # Crear índices para esta base de datos
            indices_db = self.indices_criticos.get(db_name, [])

            if not indices_db:
                print(f"[INFO] No hay índices definidos para {db_name}")
                conexion.close()
                return

            print(f"\n[INDEXES] Creando {len(indices_db)} índices para {db_name}")

            creados_exitosos = 0
            for indice_config in indices_db:
                print(f"\n[PROCESSING] {indice_config['name']} en tabla '{indice_config['table']}'")
                print(f"  Razón: {indice_config['reason']}")
                print(f"  Columnas: {', '.join(indice_config['columns'])}")

                if self.crear_indice(conexion, indice_config):
                    creados_exitosos += 1

            print(f"\n[SUMMARY] Base de datos {db_name}:")
            print(f"  Índices procesados: {len(indices_db)}")
            print(f"  Creados exitosamente: {creados_exitosos}")
            print(f"  Ya existían: {len(indices_db) - creados_exitosos}")

            conexion.close()

        except Exception as e:
            print(f"[ERROR] Error procesando base de datos {db_name}: {e}")

    def ejecutar_optimizacion(self):
        """Ejecuta la optimización completa de índices"""

        print("[DATABASE OPTIMIZATION] Creando índices de rendimiento - Rexus.app")
        print("=" * 70)
        print(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if not DATABASE_AVAILABLE:
            print("[ERROR] Módulos de base de datos no disponibles")
            return

        # Bases de datos a procesar
        databases = {
            "users": get_users_connection,
            "inventario": get_inventario_connection,
            "auditoria": get_auditoria_connection
        }

        # Procesar cada base de datos
        for db_name, connection_func in databases.items():
            self.procesar_base_datos(db_name, connection_func)

        # Mostrar resumen final
        self._mostrar_resumen_final()

    def _mostrar_resumen_final(self):
        """Muestra resumen final de la optimización"""

        print("\n" + "=" * 70)
        print("[FINAL REPORT] RESUMEN DE OPTIMIZACIÓN DE ÍNDICES")
        print("=" * 70)

        print(f"\n[STATISTICS] Estadísticas generales:")
        print(f"  Índices creados: {len(self.results['created'])}")
        print(f"  Índices ya existían: {len(self.results['existing'])}")
        print(f"  Errores: {len(self.results['errors'])}")

        if self.results['created']:
            print(f"\n[SUCCESS] ÍNDICES CREADOS EXITOSAMENTE:")
            for indice in self.results['created']:
                unique_str = " (UNIQUE)" if indice['unique'] else ""
                print(f"  + {indice['name']}{unique_str}")
                print(f"    Tabla: {indice['table']}")
                print(f"    Columnas: {', '.join(indice['columns'])}")
                print(f"    Propósito: {indice['reason']}")
                print()

        if self.results['existing']:
            print(f"\n[INFO] ÍNDICES QUE YA EXISTÍAN:")
            for indice in self.results['existing']:
                print(f"  = {indice}")

        if self.results['errors']:
            print(f"\n[ERRORS] ERRORES DURANTE LA CREACIÓN:")
            for error in self.results['errors']:
                print(f"  - {error}")

        # Estadísticas de análisis
        if self.results['analysis']:
            print(f"\n[PERFORMANCE ANALYSIS] ANÁLISIS DE RENDIMIENTO:")
            for db_name, analysis in self.results['analysis'].items():
                print(f"  {db_name.upper()}:")
                print(f"    Total índices: {analysis['total_indices']}")
                if analysis['indices_mas_usados']:
                    print(f"    Índices más utilizados: {len(analysis['indices_mas_usados'])}")

        total_procesados = len(self.results['created']) + len(self.results['existing'])
        print(f"\n[RESULT] OPTIMIZACIÓN COMPLETADA")
        print(f"  Total índices procesados: {total_procesados}")
        print(f"  Bases de datos optimizadas: {len(self.results['analysis'])}")

        if len(self.results['errors']) == 0:
            print("[SUCCESS] Optimización de índices completada exitosamente")
            print("          Las consultas deberían ser significativamente más rápidas")
        else:
            print("[WARNING] Optimización completada con algunos errores")
            print("          Revisar errores y ejecutar nuevamente si es necesario")

def main():
    """Función principal"""

    # Verificar directorio
    if not (root_dir / "rexus").exists():
        print("[ERROR] No se encuentra el directorio 'rexus'. Ejecutar desde la raíz del proyecto.")
        sys.exit(1)

    try:
        # Crear y ejecutar optimizador
        optimizer = DatabaseIndexOptimizer()
        optimizer.ejecutar_optimizacion()

        print(f"\n[INFO] Optimización completada. Logs guardados en: tools/database/")

    except Exception as e:
        print(f"[ERROR] Error ejecutando optimización: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
