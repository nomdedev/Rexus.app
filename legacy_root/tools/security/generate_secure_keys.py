#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2024 Rexus.app

Generador de claves seguras para configuración de producción
"""

import secrets
import os
from pathlib import Path


def generate_secure_key(length: int = 32) -> str:
    """
    Genera una clave segura usando el módulo secrets.

    Args:
        length: Longitud de la clave en bytes (default: 32)

    Returns:
        Clave hexadecimal segura
    """
    return secrets.token_hex(length)


def generate_env_keys() -> dict:
    """
    Genera todas las claves necesarias para el archivo .env

    Returns:
        Dict con todas las claves generadas
    """
    return {
        'SECRET_KEY': generate_secure_key(32),
        'JWT_SECRET_KEY': generate_secure_key(32),
        'ENCRYPTION_KEY': generate_secure_key(32),
        'PASSWORD_SALT': generate_secure_key(16),
        'DB_PASSWORD': generate_secure_key(16),  # Para BD si se necesita
    }


def create_secure_env_file():
    """Crea un archivo .env con claves seguras generadas."""

    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent
    env_file = project_root / '.env'
    env_example_file = project_root / '.env.example'

    print("=" * 80)
    print("GENERADOR DE CLAVES SEGURAS - REXUS.APP")
    print("=" * 80)

    if env_file.exists():
        response = input(f"\nEl archivo .env ya existe en {env_file}\n¿Desea sobrescribirlo? (s/N): ")
        if response.lower() not in ['s', 'si', 'y', 'yes']:
            print("Operación cancelada.")
            return False

    # Generar claves
    print("\nGenerando claves seguras...")
    keys = generate_env_keys()

    # Leer plantilla
    if not env_example_file.exists():
        print(f"ERROR: Archivo .env.example no encontrado en {env_example_file}")
        return False

    with open(env_example_file, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # Reemplazar placeholders con claves reales
    env_content = template_content
    replacements = {
        'your_secret_key_here_generate_with_secrets_token_hex_32': keys['SECRET_KEY'],
        'your_jwt_secret_key_here_generate_with_secrets_token_hex_32': keys['JWT_SECRET_KEY'],
        'your_encryption_key_here_generate_with_secrets_token_hex_32': keys['ENCRYPTION_KEY'],
        'your_secure_db_password_here': keys['DB_PASSWORD'],
        'your_dev_password_here': generate_secure_key(8),  # Más corta para dev
        'your_emergency_password_here': generate_secure_key(12),
        'demo_secure_admin_2025': generate_secure_key(8),
        'demo_secure_supervisor_2025': generate_secure_key(8),
        'demo_secure_operador_2025': generate_secure_key(8),
        'demo_secure_contador_2025': generate_secure_key(8),
    }

    for placeholder, secure_key in replacements.items():
        env_content = env_content.replace(placeholder, secure_key)

    # Escribir archivo .env
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)

        print(f"\n✅ Archivo .env creado exitosamente en {env_file}")
        print("\n🔐 Claves generadas:")
        for key_name, key_value in keys.items():
            print(f"   {key_name}: {key_value[:8]}...{key_value[-8:]}")

        print("\n⚠️  IMPORTANTE:")
        print("   • Mantenga estas claves en secreto")
        print("   • No las comparta ni las suba a repositorios")
        print("   • Haga backup seguro de estas claves")
        print("   • El archivo .env está incluido en .gitignore")

        return True

    except Exception as e:
        print(f"\n❌ Error creando archivo .env: {e}")
        return False


def display_manual_keys():
    """Muestra claves generadas para configuración manual."""

    print("=" * 80)
    print("CLAVES SEGURAS PARA CONFIGURACIÓN MANUAL")
    print("=" * 80)

    keys = generate_env_keys()

    print("\nCopie estas líneas a su archivo .env:")
    print("-" * 50)

    for key_name, key_value in keys.items():
        print(f"{key_name}={key_value}")

    print("-" * 50)
    print("\nComandos para generar nuevas claves cuando necesite:")
    print("python -c \"import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')\";")
    print("python -c \"import secrets; print(f'JWT_SECRET_KEY={secrets.token_hex(32)}')\";")
    print("python -c \"import secrets; print(f'ENCRYPTION_KEY={secrets.token_hex(32)}')\";")


def validate_existing_keys():
    """Valida las claves existentes en el archivo .env actual."""

    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent
    env_file = project_root / '.env'

    if not env_file.exists():
        print(f"\n❌ No se encontró archivo .env en {env_file}")
        return False

    print("\n🔍 Validando claves existentes...")

    # Leer archivo .env
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content = f.read()

    # Verificar claves críticas
    critical_keys = ['SECRET_KEY', 'JWT_SECRET_KEY', 'ENCRYPTION_KEY']
    weak_patterns = [
        'your_', 'default_', 'test_', 'demo_', 'example_',
        'change_me', 'replace_me', 'secret', '12345'
    ]

    issues = []

    for key in critical_keys:
        # Buscar la clave en el archivo
        import re
        pattern = rf'^{key}=(.+)$'
        match = re.search(pattern, env_content, re.MULTILINE)

        if not match:
            issues.append(f"❌ Clave {key} no encontrada")
            continue

        value = match.group(1).strip()

        # Verificar longitud
        if len(value) < 32:
            issues.append(f"⚠️  Clave {key} muy corta ({len(value)} caracteres, mínimo 32)")

        # Verificar patrones débiles
        if any(pattern in value.lower() for pattern in weak_patterns):
            issues.append(f"🚨 Clave {key} usa patrones inseguros")

        # Verificar entropía básica
        if len(set(value)) < 8:
            issues.append(f"⚠️  Clave {key} tiene poca diversidad de caracteres")

    if issues:
        print("\n🚨 PROBLEMAS DE SEGURIDAD ENCONTRADOS:")
        for issue in issues:
            print(f"   {issue}")
        print("\n💡 Recomendación: Regenere las claves usando este script")
        return False
    else:
        print("\n✅ Todas las claves son seguras")
        return True


def main():
    """Función principal."""

    print("OPCIONES:")
    print("1. Generar archivo .env completo con claves seguras")
    print("2. Mostrar solo las claves para configuración manual")
    print("3. Validar claves existentes")
    print("4. Salir")

    while True:
        choice = input("\nSeleccione una opción (1-4): ").strip()

        if choice == '1':
            create_secure_env_file()
            break
        elif choice == '2':
            display_manual_keys()
            break
        elif choice == '3':
            validate_existing_keys()
            break
        elif choice == '4':
            print("Saliendo...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")


if __name__ == "__main__":
    main()
