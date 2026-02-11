"""
Script de Migración de Contraseñas - Rexus.app
Migra hashes SHA-256 legacy a bcrypt/Argon2/PBKDF2 seguros

Uso:
    python -m rexus.utils.password_migration --dry-run
    python -m rexus.utils.password_migration --migrate
    python -m rexus.utils.password_migration --verify
"""

import argparse
import hashlib
import logging
import sys
from datetime import datetime
from typing import Dict, List, Tuple

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PasswordMigrationManager:
    """Gestor de migración de contraseñas SHA-256 a métodos seguros."""

    def __init__(self, db_connection=None):
        """
        Inicializa el gestor de migración.

        Args:
            db_connection: Conexión a la base de datos (opcional)
        """
        self.db_connection = db_connection
        self.stats = {
            'total_users': 0,
            'legacy_hashes': 0,
            'migrated': 0,
            'errors': 0,
            'already_secure': 0
        }

    def detect_hash_type(self, password_hash: str) -> str:
        """
        Detecta el tipo de hash usado.

        Args:
            password_hash: Hash almacenado

        Returns:
            Tipo de hash ('argon2', 'bcrypt', 'pbkdf2', 'sha256_legacy', 'unknown')
        """
        if not password_hash:
            return 'unknown'

        if password_hash.startswith('argon2$'):
            return 'argon2'
        elif password_hash.startswith('bcrypt$'):
            return 'bcrypt'
        elif password_hash.startswith('pbkdf2$'):
            return 'pbkdf2'
        elif password_hash.startswith('$2b$') or password_hash.startswith('$2a$'):
            return 'bcrypt'
        elif len(password_hash) == 64 and all(c in '0123456789abcdef' for c in password_hash.lower()):
            return 'sha256_legacy'
        else:
            return 'unknown'

    def is_legacy_hash(self, password_hash: str) -> bool:
        """
        Verifica si el hash es un SHA-256 legacy que necesita migración.

        Args:
            password_hash: Hash almacenado

        Returns:
            True si es un hash legacy
        """
        hash_type = self.detect_hash_type(password_hash)
        return hash_type == 'sha256_legacy'

    def scan_users(self) -> List[Dict]:
        """
        Escanea todos los usuarios para identificar hashes legacy.

        Returns:
            Lista de usuarios con hashes legacy
        """
        legacy_users = []

        try:
            if not self.db_connection:
                logger.error("No hay conexión a base de datos")
                return legacy_users

            cursor = self.db_connection.cursor()

            # Obtener todos los usuarios con sus hashes
            cursor.execute("""
                SELECT id, usuario, password_hash, rol, email
                FROM usuarios
                WHERE estado = 'activo'
            """)

            users = cursor.fetchall()
            self.stats['total_users'] = len(users)

            for user in users:
                user_id, usuario, password_hash, rol, email = user
                hash_type = self.detect_hash_type(password_hash)

                user_info = {
                    'id': user_id,
                    'usuario': usuario,
                    'current_hash': password_hash[:20] + '...',  # Solo mostrar primeros 20 chars
                    'hash_type': hash_type,
                    'is_legacy': self.is_legacy_hash(password_hash),
                    'rol': rol,
                    'email': email
                }

                if hash_type == 'sha256_legacy':
                    self.stats['legacy_hashes'] += 1
                    legacy_users.append(user_info)
                elif hash_type in ['argon2', 'bcrypt', 'pbkdf2']:
                    self.stats['already_secure'] += 1

            cursor.close()

        except Exception as e:
            logger.error(f"Error escaneando usuarios: {e}")

        return legacy_users

    def migrate_user_password(self, user_id: int, current_hash: str) -> bool:
        """
        Migra la contraseña de un usuario de SHA-256 a un método seguro.

        NOTA: Esta operación requiere que el usuario proporcione su contraseña
        actual porque no podemos revertir el hash SHA-256. Se implementa como
        parte del flujo de login normal.

        Args:
            user_id: ID del usuario
            current_hash: Hash actual (SHA-256)

        Returns:
            True si se migró correctamente
        """
        logger.warning(f"La migración directa no es posible para usuario ID {user_id}. "
                      "La migración ocurrirá durante el próximo login del usuario.")
        return False

    def migrate_on_login(self, username: str, password: str, db_connection) -> bool:
        """
        Migra la contraseña durante el proceso de login.

        Este método se llama después de verificar exitosamente la contraseña
        con el método legacy.

        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            db_connection: Conexión a la base de datos

        Returns:
            True si se migró correctamente
        """
        try:
            from rexus.utils.password_security import hash_password_secure

            # Generar nuevo hash seguro
            new_hash = hash_password_secure(password, method="auto")

            cursor = db_connection.cursor()

            # Actualizar el hash en la base de datos
            cursor.execute("""
                UPDATE usuarios
                SET password_hash = ?,
                    password_migrated_at = GETDATE()
                WHERE usuario = ?
            """, (new_hash, username))

            db_connection.commit()
            cursor.close()

            logger.info(f"Contraseña migrada exitosamente para usuario: {username}")
            return True

        except Exception as e:
            logger.error(f"Error migrando contraseña para {username}: {e}")
            if db_connection:
                try:
                    db_connection.rollback()
                except:
                    pass
            return False

    def verify_migration(self) -> Tuple[int, int]:
        """
        Verifica el estado de la migración.

        Returns:
            (total_migrated, total_legacy)
        """
        try:
            if not self.db_connection:
                return 0, 0

            cursor = self.db_connection.cursor()

            # Contar usuarios por tipo de hash
            cursor.execute("""
                SELECT
                    COUNT(CASE WHEN password_hash LIKE 'argon2$%' OR password_hash LIKE 'bcrypt$%'
                               OR password_hash LIKE 'pbkdf2$%' OR password_hash LIKE '$2b$%' OR password_hash LIKE '$2a$%'
                               THEN 1 END) as secure_count,
                    COUNT(CASE WHEN LEN(password_hash) = 64
                               AND password_hash NOT LIKE '%$'
                               THEN 1 END) as legacy_count
                FROM usuarios
                WHERE estado = 'activo'
            """)

            result = cursor.fetchone()
            cursor.close()

            return result[0], result[1]

        except Exception as e:
            logger.error(f"Error verificando migración: {e}")
            return 0, 0

    def generate_migration_report(self) -> str:
        """
        Genera un reporte detallado de la migración.

        Returns:
            Reporte en formato markdown
        """
        report = f"""
# Reporte de Migración de Contraseñas
**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Estadísticas

| Métrica | Cantidad |
|---------|----------|
| Total Usuarios Activos | {self.stats['total_users']} |
| Hashes Legacy (SHA-256) | {self.stats['legacy_hashes']} |
| Hashes Seguros | {self.stats['already_secure']} |
| Migrados | {self.stats['migrated']} |
| Errores | {self.stats['errors']} |

## Estado de Seguridad

"""

        if self.stats['legacy_hashes'] == 0:
            report += "✅ **Todos los usuarios usan hashes seguros**\n"
        else:
            percentage = (self.stats['legacy_hashes'] / self.stats['total_users'] * 100) if self.stats['total_users'] > 0 else 0
            report += f"⚠️ **{self.stats['legacy_hashes']} usuarios ({percentage:.1f}%) aún usan SHA-256 legacy**\n\n"
            report += "### Acción Recomendada\n\n"
            report += "Los hashes legacy se migrarán automáticamente cuando los usuarios inicien sesión. "
            report += "Para acelerar el proceso, se puede:\n"
            report += "1. Notificar a los usuarios que cambien su contraseña\n"
            report += "2. Forzar el cambio de contraseña en el próximo login\n"
            report += "3. Ejecutar una campaña de actualización de credenciales\n"

        return report


def main():
    """Función principal para ejecución desde línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Migración de contraseñas SHA-256 a métodos seguros'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Solo escanea sin realizar cambios'
    )
    parser.add_argument(
        '--migrate',
        action='store_true',
        help='Ejecuta la migración (requiere interacción de usuarios)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verifica el estado de la migración'
    )

    args = parser.parse_args()

    # Importar conexión a base de datos
    try:
        from rexus.core.database import get_users_connection
        db = get_users_connection()

        if not db.connection:
            logger.error("No se pudo conectar a la base de datos")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        sys.exit(1)

    # Crear gestor de migración
    migrator = PasswordMigrationManager(db.connection)

    if args.dry_run or len(sys.argv) == 1:
        # Escanear usuarios
        logger.info("Escaneando usuarios...")
        legacy_users = migrator.scan_users()

        print("\n" + "="*60)
        print(f"Total usuarios: {migrator.stats['total_users']}")
        print(f"Usuarios con hash legacy: {migrator.stats['legacy_hashes']}")
        print(f"Usuarios con hash seguro: {migrator.stats['already_secure']}")
        print("="*60 + "\n")

        if legacy_users:
            print("Usuarios que necesitan migración:")
            print("-" * 60)
            for user in legacy_users[:10]:  # Mostrar solo los primeros 10
                print(f"  - {user['usuario']} (ID: {user['id']}, Rol: {user['rol']})")

            if len(legacy_users) > 10:
                print(f"  ... y {len(legacy_users) - 10} más")

        # Generar reporte
        print(migrator.generate_migration_report())

    elif args.verify:
        secure, legacy = migrator.verify_migration()
        print(f"\nEstado de Migración:")
        print(f"  ✅ Hashes seguros: {secure}")
        print(f"  ⚠️  Hashes legacy: {legacy}")
        print(f"  📊 Progreso: {secure}/{secure + legacy} ({secure/(secure+legacy)*100:.1f}%)" if (secure + legacy) > 0 else "Sin datos")

    elif args.migrate:
        logger.info("La migración automática no es posible sin las contraseñas en texto plano.")
        logger.info("Los hashes se migrarán automáticamente cuando los usuarios inicien sesión.")
        logger.info("Use --dry-run para ver el estado actual.")

    # Cerrar conexión
    try:
        db.connection.close()
    except:
        pass


if __name__ == '__main__':
    main()
