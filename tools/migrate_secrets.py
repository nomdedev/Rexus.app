#!/usr/bin/env python3
"""
Script de Migración de Secrets - Rexus.app
Migra secrets desde .env a un sistema seguro

Uso:
    # Análisis (dry-run)
    python tools/migrate_secrets.py --dry-run

    # Migrar a backend local cifrado
    python tools/migrate_secrets.py --migrate --backend local

    # Migrar a Vault
    python tools/migrate_secrets.py --migrate --backend vault

    # Verificar estado
    python tools/migrate_secrets.py --verify

    # Rotar secrets
    python tools/migrate_secrets.py --rotate --key database/password
"""

import argparse
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))


def analyze_env_file(env_path: str = ".env") -> dict:
    """
    Analiza el archivo .env y detecta secrets potencialmente sensibles.

    Args:
        env_path: Ruta al archivo .env

    Returns:
        Diccionario con análisis de secrets
    """
    secrets_by_category = {
        'critical': [],      # Contraseñas, tokens, claves privadas
        'sensitive': [],     # URLs de conexión, datos personales
        'config': [],        # Configuración no sensible
        'unknown': []        # No categorizados
    }

    if not os.path.exists(env_path):
        logger.error(f"Archivo .env no encontrado: {env_path}")
        return secrets_by_category

    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip comentarios y líneas vacías
            if not line or line.startswith('#'):
                continue

            if '=' in line:
                key = line.split('=')[0].strip()

                # Categorizar por nombre
                key_lower = key.lower()

                if any(keyword in key_lower for keyword in [
                    'password', 'passwd', 'pwd', 'secret', 'key',
                    'token', 'private', 'credential', 'auth'
                ]):
                    secrets_by_category['critical'].append(key)

                elif any(keyword in key_lower for keyword in [
                    'connection', 'server', 'host', 'url', 'database',
                    'email', 'username', 'user'
                ]):
                    secrets_by_category['sensitive'].append(key)

                else:
                    secrets_by_category['config'].append(key)

    return secrets_by_category


def migrate_to_local_backend(env_path: str = ".env", delete_after: bool = False) -> dict:
    """
    Migra secrets desde .env a backend local cifrado.

    Args:
        env_path: Ruta al archivo .env
        delete_after: Si eliminar el archivo .env después de migrar

    Returns:
        Diccionario con resultados
    """
    from rexus.core.secrets_manager import SecretsManager, LocalEncryptedBackend

    results = {
        'migrated': [],
        'failed': [],
        'skipped': []
    }

    # Crear backend con una clave maestra
    master_key = os.getenv("SECRETS_MASTER_KEY")
    backend = LocalEncryptedBackend(master_key=master_key)
    manager = SecretsManager(backend=backend)

    if not os.path.exists(env_path):
        logger.error(f"Archivo .env no encontrado: {env_path}")
        return results

    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            if '=' in line:
                key = line.split('=')[0].strip()
                value = line.split('=', 1)[1].strip()

                # Convertir clave de ENV a formato de secret
                # EJ: DB_SERVER -> database/server
                secret_key = key.lower().replace('_', '/')

                try:
                    if manager.set_secret(secret_key, value):
                        results['migrated'].append(key)
                        logger.info(f"Migrado: {key}")
                    else:
                        results['failed'].append(key)
                except Exception as e:
                    logger.error(f"Error migrando {key}: {e}")
                    results['failed'].append(key)

    # Eliminar .env si se solicitó
    if delete_after and results['migrated']:
        backup_path = f"{env_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(env_path, backup_path)
        logger.info(f"Archivo .env respaldado en: {backup_path}")

    return results


def migrate_to_vault(env_path: str = ".env", delete_after: bool = False) -> dict:
    """
    Migra secrets desde .env a HashiCorp Vault.

    Args:
        env_path: Ruta al archivo .env
        delete_after: Si eliminar el archivo .env después de migrar

    Returns:
        Diccionario con resultados
    """
    from rexus.core.secrets_manager import SecretsManager, VaultBackend

    results = {
        'migrated': [],
        'failed': [],
        'skipped': []
    }

    # Verificar configuración de Vault
    vault_addr = os.getenv("VAULT_ADDR")
    vault_token = os.getenv("VAULT_TOKEN")

    if not vault_addr or not vault_token:
        logger.error("VAULT_ADDR y VAULT_TOKEN deben estar configurados")
        return results

    backend = VaultBackend()
    manager = SecretsManager(backend=backend)

    if not os.path.exists(env_path):
        logger.error(f"Archivo .env no encontrado: {env_path}")
        return results

    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            if '=' in line:
                key = line.split('=')[0].strip()
                value = line.split('=', 1)[1].strip()

                secret_key = key.lower().replace('_', '/')

                try:
                    if manager.set_secret(secret_key, value):
                        results['migrated'].append(key)
                        logger.info(f"Migrado a Vault: {key}")
                    else:
                        results['failed'].append(key)
                except Exception as e:
                    logger.error(f"Error migrando {key} a Vault: {e}")
                    results['failed'].append(key)

    if delete_after and results['migrated']:
        backup_path = f"{env_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(env_path, backup_path)
        logger.info(f"Archivo .env respaldado en: {backup_path}")

    return results


def verify_migration() -> dict:
    """
    Verifica el estado de la migración.

    Returns:
        Diccionario con estado de migración
    """
    from rexus.core.secrets_manager import get_secrets_manager

    manager = get_secrets_manager()
    secrets = manager.list_secrets()

    return {
        'total_secrets': len(secrets),
        'secrets': secrets,
        'backend': type(manager.backend).__name__
    }


def rotate_secret(key: str, new_value: str = None) -> dict:
    """
    Rota un secret específico.

    Args:
        key: Clave del secret a rotar
        new_value: Nuevo valor (opcional, genera uno si no se proporciona)

    Returns:
        Diccionario con resultado
    """
    from rexus.core.secrets_manager import get_secrets_manager

    manager = get_secrets_manager()

    if not manager.get_secret(key):
        return {
            'success': False,
            'error': f"Secret '{key}' not found"
        }

    try:
        if manager.rotate_secret(key, new_value):
            new_val = manager.get_secret(key)
            return {
                'success': True,
                'key': key,
                'new_value_preview': f"{new_val[:4]}...{new_val[-4:]}" if new_val else None
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def check_rotation_status() -> dict:
    """
    Verifica qué secrets necesitan rotación.

    Returns:
        Diccionario con secrets que necesitan rotación
    """
    from rexus.core.secrets_manager import get_secrets_manager

    manager = get_secrets_manager()
    all_secrets = manager.list_secrets()

    needs_rotation = []
    for secret_key in all_secrets:
        if manager.check_rotation_needed(secret_key, max_age_days=90):
            needs_rotation.append(secret_key)

    return {
        'total_secrets': len(all_secrets),
        'needs_rotation': len(needs_rotation),
        'secrets_to_rotate': needs_rotation
    }


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Migra secrets desde .env a un sistema seguro'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Analiza el archivo .env sin realizar cambios'
    )
    parser.add_argument(
        '--migrate',
        action='store_true',
        help='Ejecuta la migración de secrets'
    )
    parser.add_argument(
        '--backend',
        choices=['local', 'vault'],
        default='local',
        help='Backend a usar para almacenar secrets'
    )
    parser.add_argument(
        '--delete-after',
        action='store_true',
        help='Elimina el archivo .env después de migrar (hace backup)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verifica el estado de la migración'
    )
    parser.add_argument(
        '--rotate',
        action='store_true',
        help='Rota secrets que lo necesiten'
    )
    parser.add_argument(
        '--key',
        type=str,
        help='Clave específica para rotar'
    )
    parser.add_argument(
        '--env-file',
        type=str,
        default='.env',
        help='Ruta al archivo .env'
    )

    args = parser.parse_args()

    if args.dry_run:
        print("\n" + "="*60)
        print("ANÁLISIS DE SECRETS EN ARCHIVO .env")
        print("="*60 + "\n")

        analysis = analyze_env_file(args.env_file)

        print(f"Secrets críticos (contraseñas, tokens, claves): {len(analysis['critical'])}")
        for key in analysis['critical']:
            print(f"  🔴 {key}")

        print(f"\nSecrets sensibles (conexiones, usuarios): {len(analysis['sensitive'])}")
        for key in analysis['sensitive']:
            print(f"  🟡 {key}")

        print(f"\nConfiguración (no sensible): {len(analysis['config'])}")
        for key in analysis['config'][:5]:  # Mostrar solo primeros 5
            print(f"  ⚪ {key}")
        if len(analysis['config']) > 5:
            print(f"  ... y {len(analysis['config']) - 5} más")

        total = len(analysis['critical']) + len(analysis['sensitive'])
        print(f"\n⚠️  Total de secrets que migrar: {total}")
        print("="*60 + "\n")

    elif args.migrate:
        print("\n" + "="*60)
        print(f"MIGRANDO SECRETS A BACKEND {args.backend.upper()}")
        print("="*60 + "\n")

        if args.backend == 'local':
            results = migrate_to_local_backend(args.env_file, args.delete_after)
        else:
            results = migrate_to_vault(args.env_file, args.delete_after)

        print(f"\nResultados:")
        print(f"  ✅ Migrados: {len(results['migrated'])}")
        print(f"  ❌ Fallidos: {len(results['failed'])}")

        if results['failed']:
            print("\nSecrets que fallaron:")
            for key in results['failed']:
                print(f"  - {key}")

        print("="*60 + "\n")

    elif args.verify:
        status = verify_migration()

        print("\n" + "="*60)
        print("ESTADO DE MIGRACIÓN DE SECRETS")
        print("="*60 + "\n")

        print(f"Backend: {status['backend']}")
        print(f"Total de secrets: {status['total_secrets']}")

        if status['secrets']:
            print("\nSecrets almacenados:")
            for key in status['secrets'][:10]:
                print(f"  - {key}")
            if len(status['secrets']) > 10:
                print(f"  ... y {len(status['secrets']) - 10} más")

        print("="*60 + "\n")

    elif args.rotate:
        if args.key:
            result = rotate_secret(args.key)
            if result.get('success'):
                print(f"✅ Secret '{args.key}' rotado exitosamente")
            else:
                print(f"❌ Error rotando secret: {result.get('error')}")
        else:
            status = check_rotation_status()

            print("\n" + "="*60)
            print("ESTADO DE ROTACIÓN DE SECRETS")
            print("="*60 + "\n")

            print(f"Total secrets: {status['total_secrets']}")
            print(f"Necesitan rotación: {status['needs_rotation']}")

            if status['secrets_to_rotate']:
                print("\nSecrets a rotar:")
                for key in status['secrets_to_rotate']:
                    print(f"  🔄 {key}")

            print("="*60 + "\n")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
