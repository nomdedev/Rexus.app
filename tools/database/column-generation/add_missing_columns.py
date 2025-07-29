#!/usr/bin/env python3
"""
Generador de Columnas Faltantes - Rexus.app

Propósito: Agrega columnas faltantes detectadas por el validador de esquemas
Uso: python add_missing_columns.py --module=obras --table=obras --execute=false
Autor: Sistema Rexus
Fecha: 2025-01-29
"""

import os
import sys
import logging
import argparse
import pyodbc
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

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

class ColumnGenerator:
    """Generador seguro de columnas faltantes."""
    
    def __init__(self):
        self.connection = None
        self.column_definitions = self._load_column_definitions()
    
    def _load_column_definitions(self) -> Dict[str, Dict[str, str]]:
        """Define tipos de datos para columnas comunes."""
        return {
            # Columnas de identificación
            'id': 'INT IDENTITY(1,1) PRIMARY KEY',
            'codigo': 'NVARCHAR(50) NOT NULL UNIQUE',
            'nombre': 'NVARCHAR(255) NOT NULL',
            'descripcion': 'NVARCHAR(MAX) NULL',
            
            # Columnas de fechas
            'created_at': 'DATETIME2 DEFAULT GETDATE()',
            'updated_at': 'DATETIME2 NULL',
            'fecha_inicio': 'DATE NULL',
            'fecha_fin': 'DATE NULL',
            'fecha_fin_estimada': 'DATE NULL',
            'ultimo_acceso': 'DATETIME2 NULL',
            
            # Columnas de contacto
            'email': 'NVARCHAR(255) NULL',
            'telefono': 'NVARCHAR(50) NULL',
            'telefono_contacto': 'NVARCHAR(50) NULL',
            'email_contacto': 'NVARCHAR(255) NULL',
            'direccion': 'NVARCHAR(500) NULL',
            'ubicacion': 'NVARCHAR(255) NULL',
            
            # Columnas numéricas
            'precio': 'DECIMAL(18,2) DEFAULT 0',
            'precio_compra': 'DECIMAL(18,2) DEFAULT 0',
            'precio_venta': 'DECIMAL(18,2) DEFAULT 0',
            'precio_unitario': 'DECIMAL(18,2) DEFAULT 0',
            'precio_total': 'DECIMAL(18,2) DEFAULT 0',
            'presupuesto_total': 'DECIMAL(18,2) DEFAULT 0',
            'cantidad': 'INT DEFAULT 0',
            'stock': 'INT DEFAULT 0',
            'stock_actual': 'INT DEFAULT 0',
            'stock_minimo': 'INT DEFAULT 0',
            'progreso': 'DECIMAL(5,2) DEFAULT 0',
            'descuento': 'DECIMAL(18,2) DEFAULT 0',
            'impuestos': 'DECIMAL(18,2) DEFAULT 0',
            'subtotal': 'DECIMAL(18,2) DEFAULT 0',
            'total': 'DECIMAL(18,2) DEFAULT 0',
            
            # Columnas de estado y clasificación
            'estado': 'NVARCHAR(50) DEFAULT \'ACTIVO\'',
            'tipo': 'NVARCHAR(100) NULL',
            'tipo_obra': 'NVARCHAR(100) NULL',
            'categoria': 'NVARCHAR(100) NULL',
            'prioridad': 'NVARCHAR(50) DEFAULT \'MEDIA\'',
            'activo': 'BIT DEFAULT 1',
            'rol': 'NVARCHAR(50) DEFAULT \'USUARIO\'',
            
            # Columnas de usuario y auditoría
            'usuario': 'NVARCHAR(100) NULL',
            'usuario_creacion': 'NVARCHAR(100) NULL',
            'responsable': 'NVARCHAR(255) NULL',
            'username': 'NVARCHAR(100) NOT NULL UNIQUE',
            'password': 'NVARCHAR(255) NOT NULL',
            'nombre_completo': 'NVARCHAR(255) NULL',
            
            # Columnas específicas de módulos
            'cliente': 'NVARCHAR(255) NULL',
            'proveedor': 'NVARCHAR(255) NULL',
            'observaciones': 'NVARCHAR(MAX) NULL',
            'unidad_medida': 'NVARCHAR(50) NULL',
            'material': 'NVARCHAR(100) NULL',
            'dimensiones': 'NVARCHAR(255) NULL',
            'peso': 'DECIMAL(10,3) NULL',
            'espesor': 'DECIMAL(8,2) NULL',
            'color': 'NVARCHAR(100) NULL',
            
            # Columnas de referencias (foreign keys)
            'obra_id': 'INT NULL FOREIGN KEY REFERENCES obras(id)',
            'producto_id': 'INT NULL FOREIGN KEY REFERENCES productos(id)',
            'usuario_id': 'INT NULL FOREIGN KEY REFERENCES users(id)',
            'orden_id': 'INT NULL FOREIGN KEY REFERENCES ordenes_compra(id)',
            
            # Columnas de control
            'numero_orden': 'NVARCHAR(100) NOT NULL UNIQUE',
            'referencia': 'NVARCHAR(255) NULL',
            'tipo_movimiento': 'NVARCHAR(50) NULL',
            'recibido': 'BIT DEFAULT 0',
            'permiso_lectura': 'BIT DEFAULT 1',
            'permiso_escritura': 'BIT DEFAULT 0',
            'permiso_admin': 'BIT DEFAULT 0',
            'modulo': 'NVARCHAR(100) NULL'
        }
    
    def connect_to_database(self) -> bool:
        """Conecta a la base de datos."""
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
    
    def backup_table(self, table_name: str) -> bool:
        """Crea un backup de la tabla antes de modificarla."""
        try:
            backup_name = f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            cursor = self.connection.cursor()
            
            # Verificar si la tabla tiene datos
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            if row_count > 0:
                # Crear tabla de backup
                cursor.execute(f"""
                    SELECT * INTO {backup_name}
                    FROM {table_name}
                """)
                self.connection.commit()
                logger.info(f"Backup creado: {backup_name} ({row_count} filas)")
            else:
                logger.info(f"Tabla {table_name} vacía, backup no necesario")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creando backup de {table_name}: {e}")
            return False
    
    def column_exists(self, table_name: str, column_name: str) -> bool:
        """Verifica si una columna existe en la tabla."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = ? AND COLUMN_NAME = ?
            """, (table_name, column_name))
            
            return cursor.fetchone()[0] > 0
            
        except Exception as e:
            logger.error(f"Error verificando columna {column_name}: {e}")
            return True  # Asumir que existe para evitar errores
    
    def add_column(self, table_name: str, column_name: str, execute: bool = False) -> Dict[str, Any]:
        """Agrega una columna a la tabla especificada."""
        result = {
            "table": table_name,
            "column": column_name,
            "success": False,
            "sql": "",
            "message": ""
        }
        
        try:
            # Verificar si la columna ya existe
            if self.column_exists(table_name, column_name):
                result["message"] = f"Columna {column_name} ya existe en {table_name}"
                result["success"] = True
                return result
            
            # Obtener definición de la columna
            column_def = self.column_definitions.get(column_name.lower())
            if not column_def:
                # Definición por defecto para columnas desconocidas
                column_def = "NVARCHAR(255) NULL"
                logger.warning(f"Usando definición por defecto para {column_name}")
            
            # Construir SQL
            sql = f"ALTER TABLE {table_name} ADD {column_name} {column_def}"
            result["sql"] = sql
            
            if execute:
                # Crear backup antes de modificar
                if not self.backup_table(table_name):
                    result["message"] = "Error creando backup"
                    return result
                
                # Ejecutar alteración
                cursor = self.connection.cursor()
                cursor.execute(sql)
                self.connection.commit()
                
                result["success"] = True
                result["message"] = f"Columna {column_name} agregada exitosamente"
                logger.info(f"✅ Agregada columna {column_name} a {table_name}")
            else:
                result["success"] = True
                result["message"] = f"SQL generado (no ejecutado): {sql}"
                logger.info(f"📝 SQL generado para {column_name}: {sql}")
            
        except Exception as e:
            result["message"] = f"Error agregando columna: {e}"
            logger.error(f"❌ Error agregando {column_name} a {table_name}: {e}")
        
        return result
    
    def add_multiple_columns(self, table_name: str, column_names: List[str], execute: bool = False) -> List[Dict[str, Any]]:
        """Agrega múltiples columnas a una tabla."""
        results = []
        
        logger.info(f"Agregando {len(column_names)} columnas a {table_name}")
        
        for column_name in column_names:
            result = self.add_column(table_name, column_name, execute)
            results.append(result)
        
        return results
    
    def generate_script(self, results: List[Dict[str, Any]]) -> str:
        """Genera un script SQL con todas las alteraciones."""
        script_lines = [
            "-- Script de Generación de Columnas",
            f"-- Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "-- REVISAR ANTES DE EJECUTAR",
            "",
            "USE [tu_base_de_datos];",
            "GO",
            ""
        ]
        
        current_table = None
        for result in results:
            table_name = result["table"]
            
            if table_name != current_table:
                script_lines.extend([
                    f"-- Modificaciones para tabla: {table_name}",
                    ""
                ])
                current_table = table_name
            
            if result["sql"]:
                script_lines.extend([
                    f"-- {result['message']}",
                    result["sql"] + ";",
                    ""
                ])
        
        return "\n".join(script_lines)

def main():
    parser = argparse.ArgumentParser(description='Agregar columnas faltantes')
    parser.add_argument('--table', required=True, help='Nombre de la tabla')
    parser.add_argument('--columns', help='Columnas separadas por comas')
    parser.add_argument('--execute', default='false', help='Ejecutar cambios (true/false)')
    parser.add_argument('--script', help='Archivo con script de columnas')
    
    args = parser.parse_args()
    
    generator = ColumnGenerator()
    
    if not generator.connect_to_database():
        sys.exit(1)
    
    try:
        execute_changes = args.execute.lower() == 'true'
        
        if args.columns:
            # Agregar columnas específicas
            column_names = [col.strip() for col in args.columns.split(',')]
            results = generator.add_multiple_columns(args.table, column_names, execute_changes)
        else:
            logger.error("Debe especificar --columns")
            sys.exit(1)
        
        # Mostrar resultados
        success_count = sum(1 for r in results if r["success"])
        logger.info(f"Operaciones exitosas: {success_count}/{len(results)}")
        
        # Generar script
        if results:
            script_content = generator.generate_script(results)
            script_file = Path(__file__).parent.parent / "temp-fixes" / f"add_columns_{args.table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            script_file.parent.mkdir(exist_ok=True)
            
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            logger.info(f"Script generado: {script_file}")
    
    finally:
        if generator.connection:
            generator.connection.close()
    
    logger.info("Generación completada")

if __name__ == "__main__":
    main()