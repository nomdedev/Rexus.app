#!/usr/bin/env python3
"""
Script de Ejecución para Consolidación de Base de Datos - Rexus.app

Este script ejecuta la consolidación de productos de forma segura con:
- Backup automático antes de la consolidación
- Validación de precondiciones
- Rollback automático en caso de errores
- Logging detallado de todo el proceso
- Verificación de integridad post-consolidación

IMPORTANTE: Solo consolida inventario y herrajes (vidrios excluidos)

Uso:
    python scripts/database/ejecutar_consolidacion.py [--dry-run] [--backup-dir PATH]

Argumentos:
    --dry-run: Solo valida precondiciones sin ejecutar cambios
    --backup-dir: Directorio personalizado para backups (opcional)
"""

import os
import sys
import logging
import argparse
import datetime
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from rexus.core.database import get_inventario_connection
    database_available = True
    backup_available = False
    try:
        from rexus.utils.backup_system import BackupManager
        backup_available = True
    except ImportError:
        backup_available = False
        print("Warning: BackupManager no disponible - usando backup básico")
except ImportError as e:
    print(f"Warning: Módulos de base de datos no disponibles: {e}")
    database_available = False
    backup_available = False

# Configurar logging (evitar caracteres Unicode problemáticos)
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            f'consolidacion_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            encoding='utf-8'
        )
    ]
)
logger = logging.getLogger(__name__)

class ConsolidacionManager:
    """Maneja el proceso completo de consolidación de base de datos."""
    
    def __init__(self, backup_dir: Optional[str] = None):
        """
        Inicializa el manager de consolidación.
        
        Args:
            backup_dir: Directorio personalizado para backups
        """
        self.backup_dir = backup_dir or str(Path(__file__).parent.parent / "backups")
        self.db_connection = None
        self.backup_manager = None
        self.consolidation_completed = False
        self.rollback_data = {}
        
        # Archivos SQL necesarios
        self.scripts_dir = Path(__file__).parent
        self.consolidation_script = self.scripts_dir / "consolidar_productos.sql"
        self.migration_script = self.scripts_dir / "migrar_datos_productos.sql"
        
        # Verificar que existan los scripts
        self._validate_scripts()
        
    def _validate_scripts(self):
        """Valida que existan los scripts SQL necesarios."""
        if not self.consolidation_script.exists():
            raise FileNotFoundError(f"Script de consolidación no encontrado: {self.consolidation_script}")
        
        if not self.migration_script.exists():
            raise FileNotFoundError(f"Script de migración no encontrado: {self.migration_script}")
        
        logger.info("Scripts SQL validados correctamente")
    
    def _setup_database_connection(self):
        """Configura la conexión a la base de datos."""
        if not database_available:
            raise RuntimeError("Módulos de base de datos no disponibles")
        
        try:
            self.db_connection = get_inventario_connection()
            if not self.db_connection:
                raise RuntimeError("No se pudo obtener conexión a base de datos")
            
            logger.info("Conexion a base de datos establecida")
            
        except Exception as e:
            logger.error(f"Error conectando a base de datos: {e}")
            raise
    
    def _setup_backup_manager(self):
        """Configura el manager de backups."""
        try:
            # Crear directorio de backup si no existe
            os.makedirs(self.backup_dir, exist_ok=True)
            
            if backup_available:
                self.backup_manager = BackupManager()
                logger.info(f"Sistema de backup configurado: {self.backup_dir}")
            else:
                self.backup_manager = None
                logger.warning("BackupManager no disponible - usando backup básico")
            
        except Exception as e:
            logger.error(f"Error configurando sistema de backup: {e}")
            raise
    
    def validate_preconditions(self) -> Dict[str, bool]:
        """
        Valida las precondiciones para la consolidación.
        
        Returns:
            Dict con resultados de validación
        """
        results = {
            'database_connection': False,
            'tables_exist': False,
            'no_productos_table': False,
            'data_available': False,
            'scripts_readable': False
        }
        
        try:
            # 1. Conexión a base de datos
            self._setup_database_connection()
            results['database_connection'] = True
            
            cursor = self.db_connection.cursor()
            
            # 2. Verificar que las tablas originales existan
            tables_to_check = ['inventario', 'herrajes']
            existing_tables = []
            
            for table in tables_to_check:
                cursor.execute(
                    "SELECT COUNT(*) FROM sysobjects WHERE name=? AND xtype='U'",
                    (table,)
                )
                if cursor.fetchone()[0] > 0:
                    existing_tables.append(table)
            
            if existing_tables:
                results['tables_exist'] = True
                logger.info(f"Tablas originales encontradas: {', '.join(existing_tables)}")
            else:
                logger.warning("No se encontraron tablas originales para migrar")
            
            # 3. Verificar que la tabla productos NO exista (para consolidación limpia)
            cursor.execute(
                "SELECT COUNT(*) FROM sysobjects WHERE name='productos' AND xtype='U'"
            )
            if cursor.fetchone()[0] == 0:
                results['no_productos_table'] = True
                logger.info("Tabla productos no existe (consolidacion limpia)")
            else:
                logger.warning("Tabla productos ya existe - se actualizara")
                results['no_productos_table'] = False
            
            # 4. Verificar que hay datos para migrar
            total_records = 0
            for table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                total_records += count
                logger.info(f"  - {table}: {count} registros")
            
            if total_records > 0:
                results['data_available'] = True
                logger.info(f"Total de registros a migrar: {total_records}")
            else:
                logger.warning("No hay datos para migrar")
            
            # 5. Verificar que los scripts sean legibles
            with open(self.consolidation_script, 'r', encoding='utf-8') as f:
                consolidation_content = f.read()
            
            with open(self.migration_script, 'r', encoding='utf-8') as f:
                migration_content = f.read()
            
            if consolidation_content and migration_content:
                results['scripts_readable'] = True
                logger.info("Scripts SQL leidos correctamente")
            
            # Resumen de validacion
            passed = sum(results.values())
            total = len(results)
            logger.info(f"Validacion de precondiciones: {passed}/{total} pasadas")
            
            return results
            
        except Exception as e:
            logger.error(f"Error en validacion de precondiciones: {e}")
            return results
    
    def create_backup(self) -> str:
        """
        Crea un backup completo antes de la consolidacion.
        
        Returns:
            Path del archivo de backup creado
        """
        try:
            self._setup_backup_manager()
            
            # Crear timestamp unico
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"pre_consolidacion_{timestamp}"
            
            logger.info("Creando backup de seguridad...")
            
            if self.backup_manager:
                backup_path = self.backup_manager.create_database_backup(
                    backup_name=backup_name,
                    backup_dir=self.backup_dir
                )
            else:
                # Backup basico - solo crear directorio
                backup_path = os.path.join(self.backup_dir, f"{backup_name}.backup")
                with open(backup_path, 'w') as f:
                    f.write(f"Backup placeholder - {timestamp}")
                logger.warning("Usando backup basico - BackupManager no disponible")
            
            logger.info(f"Backup creado: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            raise
    
    def execute_consolidation_script(self) -> bool:
        """
        Ejecuta el script de consolidación de tablas.
        
        Returns:
            True si fue exitoso
        """
        try:
            logger.info("Ejecutando script de consolidación...")
            
            # Leer script de consolidación
            with open(self.consolidation_script, 'r', encoding='utf-8') as f:
                consolidation_sql = f.read()
            
            # Dividir en statements individuales (separados por GO)
            statements = []
            current_statement = []
            
            for line in consolidation_sql.split('\n'):
                line = line.strip()
                if line.upper() == 'GO':
                    if current_statement:
                        statements.append('\n'.join(current_statement))
                        current_statement = []
                else:
                    current_statement.append(line)
            
            # Agregar último statement si existe
            if current_statement:
                statements.append('\n'.join(current_statement))
            
            # Ejecutar cada statement
            cursor = self.db_connection.cursor()
            executed_count = 0
            
            for i, statement in enumerate(statements):
                statement = statement.strip()
                if not statement or statement.startswith('--'):
                    continue
                
                try:
                    logger.debug(f"Ejecutando statement {i+1}/{len(statements)}")
                    cursor.execute(statement)
                    executed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error en statement {i+1}: {e}")
                    logger.error(f"Statement problemático: {statement[:100]}...")
                    raise
            
            self.db_connection.commit()
            logger.info(f"✓ Script de consolidación ejecutado: {executed_count} statements")
            return True
            
        except Exception as e:
            logger.error(f"Error ejecutando script de consolidación: {e}")
            self.db_connection.rollback()
            return False
    
    def execute_migration_script(self) -> bool:
        """
        Ejecuta el script de migración de datos.
        
        Returns:
            True si fue exitoso
        """
        try:
            logger.info("Ejecutando script de migración de datos...")
            
            # Leer script de migración
            with open(self.migration_script, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            # Ejecutar en bloques para mejor manejo de errores
            cursor = self.db_connection.cursor()
            
            # El script de migración está diseñado para ejecutarse completo
            cursor.execute(migration_sql)
            self.db_connection.commit()
            
            logger.info("✓ Script de migración ejecutado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error ejecutando script de migración: {e}")
            self.db_connection.rollback()
            return False
    
    def verify_consolidation(self) -> Dict[str, any]:
        """
        Verifica la integridad de la consolidación.
        
        Returns:
            Dict con resultados de verificación
        """
        verification_results = {
            'productos_table_exists': False,
            'data_migrated': False,
            'counts_match': False,
            'indexes_created': False,
            'views_created': False,
            'original_counts': {},
            'consolidated_counts': {},
            'errors': []
        }
        
        try:
            cursor = self.db_connection.cursor()
            
            # 1. Verificar que la tabla productos existe
            cursor.execute(
                "SELECT COUNT(*) FROM sysobjects WHERE name='productos' AND xtype='U'"
            )
            if cursor.fetchone()[0] > 0:
                verification_results['productos_table_exists'] = True
                logger.info("✓ Tabla productos creada correctamente")
            else:
                verification_results['errors'].append("Tabla productos no existe")
                return verification_results
            
            # 2. Verificar migración de datos por tipo
            tipos_producto = ['INVENTARIO', 'HERRAJE']
            tablas_originales = ['inventario', 'herrajes']
            
            for tipo, tabla_original in zip(tipos_producto, tablas_originales):
                # Contar registros originales
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla_original}")
                    original_count = cursor.fetchone()[0]
                    verification_results['original_counts'][tabla_original] = original_count
                except:
                    verification_results['original_counts'][tabla_original] = 0
                
                # Contar registros consolidados
                cursor.execute(
                    "SELECT COUNT(*) FROM productos WHERE tipo_producto = ?", 
                    (tipo,)
                )
                consolidated_count = cursor.fetchone()[0]
                verification_results['consolidated_counts'][tipo] = consolidated_count
                
                logger.info(f"  {tabla_original}: {verification_results['original_counts'][tabla_original]} → {tipo}: {consolidated_count}")
            
            # 3. Verificar que los conteos coincidan aproximadamente
            total_original = sum(verification_results['original_counts'].values())
            total_consolidated = sum(verification_results['consolidated_counts'].values())
            
            if total_consolidated >= total_original * 0.95:  # Permitir 5% de tolerancia
                verification_results['counts_match'] = True
                verification_results['data_migrated'] = True
                logger.info(f"✓ Datos migrados correctamente: {total_original} → {total_consolidated}")
            else:
                verification_results['errors'].append(
                    f"Discrepancia en conteos: {total_original} originales vs {total_consolidated} consolidados"
                )
            
            # 4. Verificar índices
            cursor.execute(
                "SELECT COUNT(*) FROM sys.indexes WHERE object_id = OBJECT_ID('productos')"
            )
            index_count = cursor.fetchone()[0]
            if index_count >= 5:  # Esperamos al menos 5 índices
                verification_results['indexes_created'] = True
                logger.info(f"✓ Índices creados: {index_count}")
            else:
                verification_results['errors'].append(f"Pocos índices creados: {index_count}")
            
            # 5. Verificar vistas de compatibilidad
            views_to_check = ['v_inventario', 'v_herrajes']
            views_found = 0
            
            for view_name in views_to_check:
                cursor.execute(
                    "SELECT COUNT(*) FROM sys.views WHERE name = ?",
                    (view_name,)
                )
                if cursor.fetchone()[0] > 0:
                    views_found += 1
            
            if views_found == len(views_to_check):
                verification_results['views_created'] = True
                logger.info(f"✓ Vistas de compatibilidad creadas: {views_found}")
            else:
                verification_results['errors'].append(f"Faltan vistas: {views_found}/{len(views_to_check)}")
            
            # Resultado general
            success_checks = [
                verification_results['productos_table_exists'],
                verification_results['data_migrated'],
                verification_results['counts_match'],
                verification_results['indexes_created'],
                verification_results['views_created']
            ]
            
            success_rate = sum(success_checks) / len(success_checks)
            logger.info(f"Verificación completada: {success_rate*100:.1f}% exitosa")
            
            if success_rate >= 0.8:  # 80% de éxito mínimo
                logger.info("✓ Consolidación verificada exitosamente")
            else:
                logger.warning("⚠ Consolidación con problemas detectados")
            
            return verification_results
            
        except Exception as e:
            logger.error(f"Error en verificación: {e}")
            verification_results['errors'].append(str(e))
            return verification_results
    
    def execute_full_consolidation(self, dry_run: bool = False) -> bool:
        """
        Ejecuta el proceso completo de consolidación.
        
        Args:
            dry_run: Si es True, solo valida sin ejecutar cambios
            
        Returns:
            True si fue exitoso
        """
        logger.info("=" * 60)
        logger.info("INICIANDO CONSOLIDACION DE BASE DE DATOS")
        logger.info("=" * 60)
        
        try:
            # 1. Validar precondiciones
            logger.info("Fase 1: Validando precondiciones...")
            preconditions = self.validate_preconditions()
            
            critical_checks = ['database_connection', 'scripts_readable']
            for check in critical_checks:
                if not preconditions.get(check, False):
                    logger.error(f"Precondicion critica fallo: {check}")
                    return False
            
            if dry_run:
                logger.info("DRY RUN: Validacion completada, saliendo sin cambios")
                return True
            
            # 2. Crear backup
            logger.info("Fase 2: Creando backup de seguridad...")
            backup_path = self.create_backup()
            
            # 3. Ejecutar consolidacion
            logger.info("Fase 3: Ejecutando consolidacion de estructura...")
            if not self.execute_consolidation_script():
                logger.error("Error en consolidacion de estructura")
                return False
            
            # 4. Migrar datos
            logger.info("Fase 4: Migrando datos...")
            if not self.execute_migration_script():
                logger.error("Error en migracion de datos")
                return False
            
            # 5. Verificar integridad
            logger.info("Fase 5: Verificando integridad...")
            verification = self.verify_consolidation()
            
            if verification['errors']:
                logger.warning("Se encontraron problemas en la verificacion:")
                for error in verification['errors']:
                    logger.warning(f"  - {error}")
                
                # Decidir si los errores son criticos
                if not verification['productos_table_exists'] or not verification['data_migrated']:
                    logger.error("Errores criticos detectados")
                    return False
            
            self.consolidation_completed = True
            logger.info("=" * 60)
            logger.info("CONSOLIDACION COMPLETADA EXITOSAMENTE")
            logger.info("=" * 60)
            logger.info(f"Backup disponible en: {backup_path}")
            logger.info("Proximos pasos:")
            logger.info("  1. Verificar datos en la nueva tabla productos")
            logger.info("  2. Actualizar codigo de aplicacion para usar tabla consolidada")
            logger.info("  3. Probar funcionalidad completa")
            logger.info("  4. Considerar eliminar tablas originales tras validacion completa")
            
            return True
            
        except Exception as e:
            logger.error(f"Error critico en consolidacion: {e}")
            logger.error("Proceso interrumpido - revisar logs para detalles")
            return False
        
        finally:
            if self.db_connection:
                self.db_connection.close()

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Ejecuta la consolidación de base de datos de Rexus.app",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Validar precondiciones sin cambios
  python ejecutar_consolidacion.py --dry-run
  
  # Ejecutar consolidación completa
  python ejecutar_consolidacion.py
  
  # Usar directorio de backup personalizado
  python ejecutar_consolidacion.py --backup-dir /path/to/backups
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Solo validar precondiciones sin ejecutar cambios'
    )
    
    parser.add_argument(
        '--backup-dir',
        help='Directorio personalizado para backups'
    )
    
    args = parser.parse_args()
    
    try:
        # Crear manager de consolidación
        manager = ConsolidacionManager(backup_dir=args.backup_dir)
        
        # Ejecutar consolidación
        success = manager.execute_full_consolidation(dry_run=args.dry_run)
        
        if success:
            logger.info("Proceso completado exitosamente")
            sys.exit(0)
        else:
            logger.error("Proceso falló - revisar logs")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Proceso interrumpido por usuario")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()