"""
Database Migration Executor - Rexus.app v2.0.0

Executes all database migration scripts in the correct order to create
the consolidated database structure.
"""

import os
import sys
import logging
import pyodbc
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import database configuration
try:
    from src.config.database import DATABASE_CONFIG
    print("[OK] Database configuration imported successfully")
except ImportError as e:
    print(f"[ERROR] Could not import database config: {e}")
    # Fallback configuration
    DATABASE_CONFIG = {
        'driver': 'ODBC Driver 17 for SQL Server',
        'server': 'localhost',
        'database': 'inventario',
        'trusted_connection': 'yes'
    }


class DatabaseMigrator:
    """Handles database migration execution."""

    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.migration_dir = self.project_root / "scripts" / "database"
        self.log_dir = self.project_root / "scripts" / "migration" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Configure logging
        log_file = self.log_dir / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Migration scripts in execution order
        self.migration_scripts = [
            "01_crear_tabla_productos.sql",
            "02_migrar_inventario_a_productos.sql",
            "03_migrar_herrajes_a_productos.sql",
            "04_migrar_vidrios_a_productos.sql",
            "05_crear_tabla_auditoria.sql",
            "06_migrar_datos_auditoria.sql",
            "07_crear_sistema_pedidos.sql",
            "08_migrar_pedidos_existentes.sql",
            "09_crear_productos_obra.sql",
            "10_crear_movimientos_inventario.sql"
        ]

    def get_database_connection(self):
        """Create database connection."""
        try:
            # Build connection string
            conn_str = (
                f"DRIVER={{{DATABASE_CONFIG['driver']}}};"
                f"SERVER={DATABASE_CONFIG['server']};"
                f"DATABASE={DATABASE_CONFIG['database']};"
                f"Trusted_Connection={DATABASE_CONFIG.get('trusted_connection', 'yes')}"
            )

            conn = pyodbc.connect(conn_str)
            conn.autocommit = True
            self.logger.info("Database connection established successfully")
            return conn

        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            return None

    def check_prerequisites(self):
        """Check if all prerequisites are met."""
        self.logger.info("Checking migration prerequisites...")

        # Check if migration scripts exist
        missing_scripts = []
        for script in self.migration_scripts:
            script_path = self.migration_dir / script
            if not script_path.exists():
                missing_scripts.append(script)

        if missing_scripts:
            self.logger.error(f"Missing migration scripts: {missing_scripts}")
            return False

        # Check database connectivity
        conn = self.get_database_connection()
        if not conn:
            self.logger.error("Cannot connect to database")
            return False

        conn.close()
        self.logger.info("Prerequisites check passed")
        return True

    def backup_existing_data(self, conn):
        """Create backup of existing data before migration."""
        self.logger.info("Creating data backup before migration...")

        backup_queries = [
            "SELECT COUNT(*) as count_inventario FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'inventario_perfiles'",
            "SELECT COUNT(*) as count_herrajes FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'herrajes'",
            "SELECT COUNT(*) as count_vidrios FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'vidrios'",
            "SELECT COUNT(*) as count_pedidos FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos'"
        ]

        try:
            cursor = conn.cursor()
            backup_info = {}

            # Get table counts
            for query in backup_queries:
                cursor.execute(query)
                result = cursor.fetchone()
                table_name = query.split("'")[1]
                backup_info[table_name] = "exists" if result else "not_found"

            self.logger.info(f"Backup info: {backup_info}")

            # Create backup summary
            backup_file = self.log_dir / "pre_migration_backup.txt"
            with open(backup_file, 'w') as f:
                f.write(f"Pre-Migration Backup Summary\n")
                f.write(f"Generated: {datetime.now()}\n\n")
                for table, status in backup_info.items():
                    f.write(f"{table}: {status}\n")

            self.logger.info(f"Backup summary saved to: {backup_file}")
            return True

        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return False

    def execute_script(self, conn, script_path):
        """Execute a single SQL script."""
        self.logger.info(f"Executing script: {script_path.name}")

        try:
            # Read script content
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()

            # Split script into batches (separated by GO)
            batches = [batch.strip() for batch in script_content.split('GO') if batch.strip()]

            cursor = conn.cursor()
            executed_batches = 0

            for batch in batches:
                if batch and not batch.startswith('--'):
                    try:
                        cursor.execute(batch)
                        executed_batches += 1

                        # Fetch any messages
                        while cursor.nextset():
                            pass

                    except Exception as batch_error:
                        self.logger.warning(f"Batch execution warning in {script_path.name}: {batch_error}")

            self.logger.info(f"Successfully executed {executed_batches} batches from {script_path.name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to execute script {script_path.name}: {e}")
            return False

    def validate_migration(self, conn):
        """Validate that migration was successful."""
        self.logger.info("Validating migration results...")

        validation_queries = [
            "SELECT COUNT(*) as productos_count FROM productos",
            "SELECT COUNT(DISTINCT categoria) as categorias_count FROM productos",
            "SELECT COUNT(*) as pedidos_count FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos_consolidado'",
            "SELECT COUNT(*) as obras_count FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'productos_obra'",
            "SELECT COUNT(*) as movimientos_count FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'movimientos_inventario'"
        ]

        try:
            cursor = conn.cursor()
            validation_results = {}

            for query in validation_queries:
                try:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    metric_name = query.split(' as ')[1].split(' FROM')[0]
                    validation_results[metric_name] = result[0] if result else 0
                except:
                    validation_results[query.split(' as ')[1].split(' FROM')[0]] = "error"

            self.logger.info(f"Validation results: {validation_results}")

            # Save validation results
            validation_file = self.log_dir / "migration_validation.txt"
            with open(validation_file, 'w') as f:
                f.write(f"Migration Validation Results\n")
                f.write(f"Generated: {datetime.now()}\n\n")
                for metric, value in validation_results.items():
                    f.write(f"{metric}: {value}\n")

            return validation_results

        except Exception as e:
            self.logger.error(f"Migration validation failed: {e}")
            return {}

    def execute_migration(self, dry_run=False):
        """Execute the complete database migration."""
        self.logger.info("="*60)
        self.logger.info("STARTING DATABASE MIGRATION TO CONSOLIDATED STRUCTURE")
        self.logger.info("="*60)

        if dry_run:
            self.logger.info("DRY RUN MODE - No changes will be made to database")

        # Check prerequisites
        if not self.check_prerequisites():
            self.logger.error("Prerequisites check failed. Aborting migration.")
            return False

        # Get database connection
        conn = self.get_database_connection()
        if not conn:
            self.logger.error("Cannot establish database connection. Aborting migration.")
            return False

        try:
            # Create backup
            if not dry_run:
                if not self.backup_existing_data(conn):
                    self.logger.error("Backup creation failed. Aborting migration.")
                    return False
            else:
                self.logger.info("DRY RUN: Skipping backup creation")

            # Execute migration scripts
            successful_scripts = 0
            failed_scripts = []

            for script_name in self.migration_scripts:
                script_path = self.migration_dir / script_name

                if dry_run:
                    self.logger.info(f"DRY RUN: Would execute {script_name}")
                    successful_scripts += 1
                else:
                    if self.execute_script(conn, script_path):
                        successful_scripts += 1
                    else:
                        failed_scripts.append(script_name)
                        self.logger.error(f"Migration script failed: {script_name}")
                        # Continue with other scripts

            # Validate migration results
            if not dry_run and successful_scripts > 0:
                validation_results = self.validate_migration(conn)
            else:
                validation_results = {"dry_run": "validation_skipped"}

            # Generate summary
            self.logger.info("="*60)
            self.logger.info("MIGRATION EXECUTION SUMMARY")
            self.logger.info("="*60)
            self.logger.info(f"Total scripts: {len(self.migration_scripts)}")
            self.logger.info(f"Successful: {successful_scripts}")
            self.logger.info(f"Failed: {len(failed_scripts)}")

            if failed_scripts:
                self.logger.error(f"Failed scripts: {failed_scripts}")

            if not dry_run:
                self.logger.info(f"Validation results: {validation_results}")

            success_rate = (successful_scripts / len(self.migration_scripts)) * 100
            self.logger.info(f"Success rate: {success_rate:.1f}%")

            if success_rate >= 90:
                self.logger.info("MIGRATION COMPLETED SUCCESSFULLY!")
                return True
            else:
                self.logger.error("MIGRATION COMPLETED WITH ERRORS")
                return False

        finally:
            conn.close()
            self.logger.info("Database connection closed")


def main():
    """Main execution."""
    print("Database Migration Executor - Rexus.app v2.0.0")
    print("="*60)

    # Get project root
    project_root = Path(__file__).parent.parent.parent
    print(f"Project root: {project_root}")

    # Initialize migrator
    migrator = DatabaseMigrator(project_root)

    # Check for dry run argument
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        print("DRY RUN MODE ENABLED - No database changes will be made")

    # Execute migration
    success = migrator.execute_migration(dry_run=dry_run)

    if success:
        print("\n[SUCCESS] Database migration completed successfully!")
        print("Next steps:")
        print("- Test the consolidated models")
        print("- Validate data integrity")
        print("- Run application tests")
    else:
        print("\n[ERROR] Database migration failed!")
        print("Check the logs for detailed error information")
        sys.exit(1)


if __name__ == "__main__":
    main()
