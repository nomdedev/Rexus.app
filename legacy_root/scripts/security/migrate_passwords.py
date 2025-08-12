#!/usr/bin/env python3
"""
Script de Migración de Contraseñas SHA-256 a PBKDF2
Rexus.app - Sistema de Seguridad Crítica

Este script actualiza todas las contraseñas SHA-256 legacy
a PBKDF2 con salt único por usuario para mejorar la seguridad.
"""

import os
import sys
import hashlib
import pyodbc
from pathlib import Path

# Agregar ruta del proyecto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rexus.utils.password_security import hash_password_secure, verify_password_secure
from rexus.utils.logging_config import get_logger

logger = get_logger('password_migration')

class PasswordMigrator:
    """Migrador de contraseñas SHA-256 legacy a PBKDF2."""
    
    def __init__(self):
        self.connection = None
        self.users_migrated = 0
        self.errors = []
        
    def connect_database(self):
        """Conecta a la base de datos."""
        try:
            # Usar variables de entorno para configuración segura
            server = os.getenv('DB_SERVER', 'ITACHI\\SQLEXPRESS')
            database = os.getenv('DB_USERS_DATABASE', 'users')
            username = os.getenv('DB_USERNAME', 'sa')
            password = os.getenv('DB_PASSWORD', '')
            driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
            
            connection_string = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"TrustServerCertificate=yes;"
            )
            
            self.connection = pyodbc.connect(connection_string)
            logger.info("Conexión a BD establecida para migración")
            return True
            
        except Exception as e:
            logger.error(f"Error conectando a BD: {e}")
            return False
    
    def is_sha256_hash(self, hash_string: str) -> bool:
        """Verifica si un hash es SHA-256 legacy."""
        if not hash_string:
            return False
        # SHA-256 produce exactamente 64 caracteres hexadecimales
        return len(hash_string) == 64 and all(c in '0123456789abcdefABCDEF' for c in hash_string)
    
    def get_legacy_users(self):
        """Obtiene usuarios con contraseñas SHA-256 legacy."""
        try:
            cursor = self.connection.cursor()
            
            # Buscar usuarios con contraseñas que parecen SHA-256
            query = """
            SELECT id, usuario, password_hash, nombre, email
            FROM usuarios 
            WHERE password_hash IS NOT NULL 
            AND LEN(password_hash) = 64
            AND password_hash NOT LIKE 'pbkdf2%'
            AND password_hash NOT LIKE 'bcrypt%'
            AND password_hash NOT LIKE 'argon2%'
            """
            
            cursor.execute(query)
            users = cursor.fetchall()
            
            logger.info(f"Encontrados {len(users)} usuarios con contraseñas legacy")
            return users
            
        except Exception as e:
            logger.error(f"Error obteniendo usuarios legacy: {e}")
            return []
    
    def create_secure_password_for_migration(self, username: str) -> str:
        """
        Crea una contraseña temporal segura para migración.
        El usuario deberá cambiarla en el primer login.
        """
        # Generar contraseña temporal basada en el usuario + timestamp
        import time
        temp_password = f"{username}_temp_{int(time.time())}"
        return hash_password_secure(temp_password, method="pbkdf2")
    
    def migrate_user_password(self, user_id: int, username: str, old_hash: str):
        """Migra la contraseña de un usuario específico."""
        try:
            cursor = self.connection.cursor()
            
            # Verificar que es realmente SHA-256
            if not self.is_sha256_hash(old_hash):
                logger.warning(f"Usuario {username}: Hash no parece SHA-256, saltando")
                return False
            
            # IMPORTANTE: Como no podemos recuperar la contraseña original de SHA-256,
            # creamos una contraseña temporal segura y marcamos para cambio obligatorio
            new_secure_hash = self.create_secure_password_for_migration(username)
            
            # Actualizar usuario con nuevo hash y flag de cambio obligatorio
            update_query = """
            UPDATE usuarios 
            SET password_hash = ?, 
                password_change_required = 1,
                last_password_change = GETDATE(),
                notes = COALESCE(notes + ' | ', '') + 'PASSWORD MIGRATED FROM SHA-256 - CHANGE REQUIRED'
            WHERE id = ?
            """
            
            cursor.execute(update_query, (new_secure_hash, user_id))
            self.connection.commit()
            
            logger.info(f"Usuario '{username}' migrado exitosamente")
            self.users_migrated += 1
            return True
            
        except Exception as e:
            error_msg = f"Error migrando usuario {username}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def run_migration(self):
        """Ejecuta la migración completa."""
        logger.info("=== INICIANDO MIGRACIÓN DE CONTRASEÑAS SHA-256 ===")
        
        if not self.connect_database():
            logger.error("FALLO: No se pudo conectar a la base de datos")
            return False
        
        try:
            # Obtener usuarios legacy
            legacy_users = self.get_legacy_users()
            
            if not legacy_users:
                logger.info("No se encontraron usuarios con contraseñas SHA-256 legacy")
                return True
            
            # Confirmar migración
            print(f"\n[ATENCION] Se van a migrar {len(legacy_users)} usuarios.")
            print("Después de la migración, todos los usuarios deberán cambiar sus contraseñas.")
            print("¿Continuar? (si/no): ", end="")
            
            response = input().lower().strip()
            if response not in ['si', 'sí', 'yes', 'y', 's']:
                logger.info("Migración cancelada por el usuario")
                return False
            
            # Migrar cada usuario
            for user_data in legacy_users:
                user_id, username, old_hash, nombre, email = user_data
                logger.info(f"Migrando usuario: {username} ({nombre})")
                self.migrate_user_password(user_id, username, old_hash)
            
            # Reporte final
            self.generate_migration_report()
            return True
            
        except Exception as e:
            logger.error(f"Error durante migración: {e}")
            return False
        
        finally:
            if self.connection:
                self.connection.close()
    
    def generate_migration_report(self):
        """Genera reporte de migración."""
        print(f"\n{'='*60}")
        print("REPORTE DE MIGRACIÓN DE CONTRASEÑAS")
        print(f"{'='*60}")
        print(f"Usuarios migrados exitosamente: {self.users_migrated}")
        print(f"Errores encontrados: {len(self.errors)}")
        
        if self.errors:
            print("\nErrores:")
            for error in self.errors:
                print(f"  - {error}")
        
        print(f"\n{'='*60}")
        print("IMPORTANTE: Actualizar auth_manager.py para usar el nuevo sistema")
        print("IMPORTANTE: Todos los usuarios deben cambiar sus contraseñas")
        print(f"{'='*60}")
        
        # Guardar reporte en archivo
        report_file = project_root / "logs" / f"password_migration_{int(__import__('time').time())}.log"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Migración de contraseñas - {__import__('datetime').datetime.now()}\n")
            f.write(f"Usuarios migrados: {self.users_migrated}\n")
            f.write(f"Errores: {len(self.errors)}\n")
            if self.errors:
                f.write("\nDetalles de errores:\n")
                for error in self.errors:
                    f.write(f"  {error}\n")
        
        logger.info(f"Reporte guardado en: {report_file}")


def main():
    """Función principal."""
    print("=" * 60)
    print("MIGRADOR DE CONTRASEÑAS SHA-256 -> PBKDF2")
    print("Rexus.app - Sistema de Seguridad Crítica")
    print("=" * 60)
    
    migrator = PasswordMigrator()
    success = migrator.run_migration()
    
    if success:
        print("\n[EXITO] MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("\n[PASOS] PRÓXIMOS PASOS REQUERIDOS:")
        print("1. Actualizar auth_manager.py para usar password_security.py")
        print("2. Notificar a usuarios sobre cambio de contraseña obligatorio")
        print("3. Ejecutar tests de seguridad para verificar funcionalidad")
        sys.exit(0)
    else:
        print("\n[ERROR] MIGRACIÓN FALLIDA")
        print("Revise los logs para más detalles")
        sys.exit(1)


if __name__ == "__main__":
    main()