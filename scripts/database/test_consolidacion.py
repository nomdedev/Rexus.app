#!/usr/bin/env python3
"""
Test Script para Consolidación de Base de Datos - Rexus.app

Este script de prueba ejecuta una validación básica de la consolidación
sin requerir conexión a base de datos real.

Uso:
    python scripts/database/test_consolidacion.py
"""

import os
import sys
import logging
import datetime
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# Configurar logging simple
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockConsolidacionManager:
    """Versión de prueba del manager de consolidación."""
    
    def __init__(self):
        """Inicializa el manager de prueba."""
        self.scripts_dir = Path(__file__).parent
        self.consolidation_script = self.scripts_dir / "consolidar_productos.sql"
        self.migration_script = self.scripts_dir / "migrar_datos_productos.sql"
        self.model_file = root_dir / "rexus" / "models" / "productos_model.py"
        
    def validate_files(self) -> bool:
        """Valida que existan los archivos necesarios."""
        logger.info("Validando archivos necesarios...")
        
        files_to_check = {
            "Script de consolidacion": self.consolidation_script,
            "Script de migracion": self.migration_script,
            "Modelo de productos": self.model_file
        }
        
        all_exist = True
        for name, file_path in files_to_check.items():
            if file_path.exists():
                logger.info(f"  - {name}: ENCONTRADO")
                # Verificar tamaño del archivo
                size = file_path.stat().st_size
                logger.info(f"    Tamaño: {size} bytes")
            else:
                logger.error(f"  - {name}: NO ENCONTRADO - {file_path}")
                all_exist = False
        
        return all_exist
    
    def validate_sql_scripts(self) -> bool:
        """Valida el contenido de los scripts SQL."""
        logger.info("Validando contenido de scripts SQL...")
        
        try:
            # Verificar script de consolidación
            with open(self.consolidation_script, 'r', encoding='utf-8') as f:
                consolidation_content = f.read()
            
            consolidation_checks = {
                "CREATE TABLE productos": "CREATE TABLE productos" in consolidation_content,
                "Índices creados": "CREATE INDEX" in consolidation_content,
                "Vistas de compatibilidad": "CREATE VIEW" in consolidation_content,
                "Triggers de auditoría": "CREATE TRIGGER" in consolidation_content,
                "Procedimientos almacenados": "CREATE PROCEDURE" in consolidation_content
            }
            
            logger.info("  Script de consolidación:")
            for check, passed in consolidation_checks.items():
                status = "OK" if passed else "FALTA"
                logger.info(f"    - {check}: {status}")
            
            # Verificar script de migración
            with open(self.migration_script, 'r', encoding='utf-8') as f:
                migration_content = f.read()
            
            migration_checks = {
                "Migración de inventario": "FROM inventario" in migration_content,
                "Migración de herrajes": "FROM herrajes" in migration_content,
                "Exclusión de vidrios": "vidrios NO se migran" in migration_content,
                "Verificación de integridad": "VERIFICANDO INTEGRIDAD" in migration_content,
                "Estadísticas de migración": "temp_migracion_summary" in migration_content
            }
            
            logger.info("  Script de migración:")
            for check, passed in migration_checks.items():
                status = "OK" if passed else "FALTA"
                logger.info(f"    - {check}: {status}")
            
            return all(consolidation_checks.values()) and all(migration_checks.values())
            
        except Exception as e:
            logger.error(f"Error validando scripts SQL: {e}")
            return False
    
    def validate_python_model(self) -> bool:
        """Valida el modelo de productos Python."""
        logger.info("Validando modelo de productos Python...")
        
        try:
            with open(self.model_file, 'r', encoding='utf-8') as f:
                model_content = f.read()
            
            model_checks = {
                "Clase ProductosModel": "class ProductosModel" in model_content,
                "Tipos de producto definidos": "TIPOS_PRODUCTO = ['INVENTARIO', 'HERRAJE', 'MATERIAL']" in model_content,
                "Método create_product": "def create_product" in model_content,
                "Método search_products": "def search_products" in model_content,
                "Método update_stock": "def update_stock" in model_content,
                "Validación de datos": "def validate_product_data" in model_content,
                "Sanitización de datos": "def _sanitize_product_data" in model_content
            }
            
            logger.info("  Modelo de productos:")
            for check, passed in model_checks.items():
                status = "OK" if passed else "FALTA"
                logger.info(f"    - {check}: {status}")
            
            return all(model_checks.values())
            
        except Exception as e:
            logger.error(f"Error validando modelo Python: {e}")
            return False
    
    def run_validation(self) -> bool:
        """Ejecuta la validación completa."""
        logger.info("=" * 60)
        logger.info("VALIDACION DE CONSOLIDACION DE BASE DE DATOS")
        logger.info("=" * 60)
        
        validations = {
            "Archivos necesarios": self.validate_files(),
            "Scripts SQL": self.validate_sql_scripts(),
            "Modelo Python": self.validate_python_model()
        }
        
        logger.info("")
        logger.info("RESUMEN DE VALIDACION:")
        logger.info("-" * 30)
        
        all_passed = True
        for validation_name, passed in validations.items():
            status = "PASÓ" if passed else "FALLÓ"
            symbol = "✓" if passed else "✗"
            try:
                logger.info(f"  {symbol} {validation_name}: {status}")
            except UnicodeEncodeError:
                # Fallback sin unicode
                symbol = "+" if passed else "-"
                logger.info(f"  {symbol} {validation_name}: {status}")
            
            if not passed:
                all_passed = False
        
        logger.info("")
        if all_passed:
            logger.info("RESULTADO: Todos los componentes de consolidación están listos")
            logger.info("PRÓXIMO PASO: Ejecutar consolidación real con conexión a BD")
        else:
            logger.error("RESULTADO: Se encontraron problemas que deben corregirse")
            logger.error("ACCIÓN: Revisar y corregir los componentes marcados como FALLÓ")
        
        logger.info("=" * 60)
        return all_passed

def main():
    """Función principal del test."""
    try:
        manager = MockConsolidacionManager()
        success = manager.run_validation()
        
        if success:
            print("\nValidación exitosa - El sistema de consolidación está listo")
            sys.exit(0)
        else:
            print("\nValidación falló - Revisar errores arriba")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nProceso interrumpido por usuario")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()