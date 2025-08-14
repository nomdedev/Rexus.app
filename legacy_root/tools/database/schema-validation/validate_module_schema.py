#!/usr/bin/env python3
"""
Validador de Esquemas de Módulos - Rexus.app

Propósito: Valida que las tablas y columnas requeridas por cada módulo existan en la BD
Uso: python validate_module_schema.py --module=obras --fix=false
Autor: Sistema Rexus
Fecha: 2025-01-29
"""

import os
import sys
import logging
import argparse
import pyodbc
from pathlib import Path
from typing import Dict, List, Any, Set

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Configurar logging
log_dir = Path(__file__).parent.parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'{Path(__file__).stem}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModuleSchemaValidator:
    """Validador de esquemas de módulos."""

    def __init__(self):
        self.connection = None
        self.module_schemas = self._load_module_schemas()

    def _load_module_schemas(self) -> Dict[str, Dict[str, List[str]]]:
        """Define esquemas esperados por módulo."""
        return {
            'obras': {
                'obras': [
                    'id', 'codigo', 'nombre', 'descripcion', 'cliente',
                    'direccion', 'telefono_contacto', 'email_contacto',
                    'fecha_inicio', 'fecha_fin_estimada', 'presupuesto_total',
                    'estado', 'tipo_obra', 'prioridad', 'responsable',
                    'observaciones', 'usuario_creacion', 'progreso',
                    'ubicacion', 'created_at', 'updated_at'
                ],
                'detalles_obra': [
                    'id', 'obra_id', 'descripcion', 'cantidad', 'precio_unitario',
                    'precio_total', 'created_at', 'updated_at'
                ]
            },
            'inventario': {
                'productos': [
                    'id', 'codigo', 'nombre', 'descripcion', 'categoria',
                    'precio_compra', 'precio_venta', 'stock_actual',
                    'stock_minimo', 'unidad_medida', 'proveedor',
                    'ubicacion', 'activo', 'created_at', 'updated_at'
                ],
                'movimientos_stock': [
                    'id', 'producto_id', 'tipo_movimiento', 'cantidad',
                    'precio_unitario', 'referencia', 'usuario',
                    'created_at'
                ]
            },
            'usuarios': {
                'users': [
                    'id', 'username', 'password', 'email', 'nombre_completo',
                    'activo', 'rol', 'ultimo_acceso', 'created_at', 'updated_at'
                ],
                'permisos': [
                    'id', 'usuario_id', 'modulo', 'permiso_lectura',
                    'permiso_escritura', 'permiso_admin', 'created_at'
                ]
            },
            'compras': {
                'ordenes_compra': [
                    'id', 'numero_orden', 'proveedor', 'fecha_orden',
                    'fecha_entrega_esperada', 'estado', 'subtotal',
                    'descuento', 'impuestos', 'total', 'observaciones',
                    'created_at', 'updated_at'
                ],
                'detalles_orden_compra': [
                    'id', 'orden_id', 'producto_id', 'cantidad',
                    'precio_unitario', 'precio_total', 'recibido'
                ]
            },
            'herrajes': {
                'herrajes': [
                    'id', 'codigo', 'nombre', 'tipo', 'material',
                    'dimensiones', 'peso', 'precio', 'stock',
                    'proveedor', 'observaciones', 'activo',
                    'created_at', 'updated_at'
                ]
            },
            'vidrios': {
                'vidrios': [
                    'id', 'codigo', 'tipo', 'espesor', 'dimensiones',
                    'color', 'precio_m2', 'stock_m2', 'proveedor',
                    'observaciones', 'activo', 'created_at', 'updated_at'
                ]
            }
        }

    def connect_to_database(self) -> bool:
        """Conecta a la base de datos usando variables de entorno."""
        try:
            server = os.getenv('DB_SERVER')
            username = os.getenv('DB_USERNAME')
            password = os.getenv('DB_PASSWORD')
            database = os.getenv('DB_NAME', 'master')

            if not all([server, username, password]):
                logger.error("Variables de entorno de BD no configuradas")
                return False

            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"TrustServerCertificate=yes;"
            )

            self.connection = pyodbc.connect(conn_str)
            logger.info("Conexión a BD establecida")
            return True

        except Exception as e:
            logger.error(f"Error conectando a BD: {e}")
            return False

    def get_existing_tables(self) -> Set[str]:
        """Obtiene las tablas existentes en la BD."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
            """)

            tables = {row[0].lower() for row in cursor.fetchall()}
            logger.info(f"Encontradas {len(tables)} tablas en BD")
            return tables

        except Exception as e:
            logger.error(f"Error obteniendo tablas: {e}")
            return set()

    def get_table_columns(self, table_name: str) -> Set[str]:
        """Obtiene las columnas de una tabla específica."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = ?
            """, (table_name,))

            columns = {row[0].lower() for row in cursor.fetchall()}
            return columns

        except Exception as e:
            logger.error(f"Error obteniendo columnas de {table_name}: {e}")
            return set()

    def validate_module(self, module_name: str) -> Dict[str, Any]:
        """Valida el esquema completo de un módulo."""
        if module_name not in self.module_schemas:
            return {"error": f"Módulo {module_name} no reconocido"}

        logger.info(f"Validando esquema del módulo: {module_name}")

        existing_tables = self.get_existing_tables()
        expected_schema = self.module_schemas[module_name]

        validation_result = {
            "module": module_name,
            "tables_status": {},
            "missing_tables": [],
            "missing_columns": {},
            "valid": True
        }

        for table_name, expected_columns in expected_schema.items():
            table_lower = table_name.lower()

            if table_lower not in existing_tables:
                validation_result["missing_tables"].append(table_name)
                validation_result["valid"] = False
                logger.warning(f"Tabla faltante: {table_name}")
                continue

            # Validar columnas
            existing_columns = self.get_table_columns(table_name)
            expected_columns_lower = {col.lower() for col in expected_columns}

            missing_columns = expected_columns_lower - existing_columns

            validation_result["tables_status"][table_name] = {
                "exists": True,
                "columns_count": len(existing_columns),
                "missing_columns": list(missing_columns)
            }

            if missing_columns:
                validation_result["missing_columns"][table_name] = list(missing_columns)
                validation_result["valid"] = False
                logger.warning(f"Columnas faltantes en {table_name}: {missing_columns}")
            else:
                logger.info(f"Tabla {table_name}: [CHECK] Esquema válido")

        return validation_result

    def generate_fix_script(self, validation_result: Dict[str, Any]) -> str:
        """Genera script SQL para corregir problemas encontrados."""
        module_name = validation_result["module"]
        script_lines = [
            f"-- Script de corrección para módulo: {module_name}",
            f"-- Generado automáticamente el {Path(__file__).stem}",
            f"-- REVISAR ANTES DE EJECUTAR",
            "",
            "USE [nombre_de_tu_base_de_datos];",
            "GO",
            ""
        ]

        # Crear tablas faltantes
        for table_name in validation_result["missing_tables"]:
            script_lines.extend([
                f"-- Crear tabla: {table_name}",
                f"-- TODO: Definir estructura completa de {table_name}",
                f"-- CREATE TABLE {table_name} (",
                f"--     id INT IDENTITY(1,1) PRIMARY KEY,",
                f"--     -- Agregar columnas específicas aquí",
                f"--     created_at DATETIME2 DEFAULT GETDATE()",
                f"-- );",
                ""
            ])

        # Agregar columnas faltantes
        for table_name, missing_columns in validation_result["missing_columns"].items():
            script_lines.append(f"-- Agregar columnas faltantes a: {table_name}")
            for column in missing_columns:
                script_lines.append(
                    f"-- ALTER TABLE {table_name} ADD {column} NVARCHAR(255) NULL;"
                )
            script_lines.append("")

        return "\n".join(script_lines)

    def save_fix_script(self, fix_script: str, module_name: str) -> str:
        """Guarda el script de corrección."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fix_{module_name}_schema_{timestamp}.sql"
        filepath = Path(__file__).parent.parent / "temp-fixes" / filename

        filepath.parent.mkdir(exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fix_script)

        logger.info(f"Script de corrección guardado: {filepath}")
        return str(filepath)

def main():
    parser = argparse.ArgumentParser(description='Validar esquema de módulo')
    parser.add_argument('--module', required=True, help='Nombre del módulo a validar')
    parser.add_argument('--fix', default='false', help='Generar script de corrección')
    parser.add_argument('--all', action='store_true', help='Validar todos los módulos')

    args = parser.parse_args()

    validator = ModuleSchemaValidator()

    if not validator.connect_to_database():
        sys.exit(1)

    try:
        if args.all:
            modules_to_validate = validator.module_schemas.keys()
        else:
            modules_to_validate = [args.module]

        for module_name in modules_to_validate:
            logger.info(f"=== Validando módulo: {module_name} ===")

            result = validator.validate_module(module_name)

            if result.get("error"):
                logger.error(result["error"])
                continue

            if result["valid"]:
                logger.info(f"[CHECK] Módulo {module_name}: Esquema válido")
            else:
                logger.warning(f"[ERROR] Módulo {module_name}: Problemas encontrados")

                if args.fix.lower() == 'true':
                    fix_script = validator.generate_fix_script(result)
                    script_path = validator.save_fix_script(fix_script, module_name)
                    logger.info(f"Script de corrección generado: {script_path}")

            print("\n" + "="*50 + "\n")

    finally:
        if validator.connection:
            validator.connection.close()

    logger.info("Validación completada")

if __name__ == "__main__":
    main()
