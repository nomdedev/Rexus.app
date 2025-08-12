#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2024 Rexus.app

Validador de configuración de variables de entorno
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rexus.utils.env_manager import env_manager


def print_separator():
    """Imprime un separador visual."""
    print("=" * 80)


def print_section(title):
    """Imprime el título de una sección."""
    print(f"\n🔍 {title}")
    print("-" * 40)


def validate_environment():
    """Valida la configuración de variables de entorno."""
    print_separator()
    print("🛡️  VALIDADOR DE CONFIGURACIÓN DE SEGURIDAD - REXUS.APP")
    print_separator()
    
    # 1. Verificar si existe el archivo .env
    print_section("Estado de archivos de configuración")
    
    env_file = Path.cwd() / '.env'
    example_file = Path.cwd() / '.env.example'
    
    if env_file.exists():
        print(f"✅ Archivo .env encontrado: {env_file}")
    else:
        print(f"⚠️  Archivo .env no encontrado: {env_file}")
        print("   💡 Copie .env.example como .env y configure las variables")
    
    if example_file.exists():
        print(f"✅ Archivo .env.example encontrado: {example_file}")
    else:
        print(f"❌ Archivo .env.example no encontrado: {example_file}")
    
    # 2. Validar modo de aplicación
    print_section("Modo de aplicación")
    
    app_env = os.getenv('APP_ENV', 'development')
    is_prod = env_manager.is_production()
    is_dev = env_manager.is_development()
    
    print(f"🏷️  Modo actual: {app_env}")
    print(f"🏭 Modo producción: {'✅ Sí' if is_prod else '❌ No'}")
    print(f"🔧 Modo desarrollo: {'✅ Sí' if is_dev else '❌ No'}")
    
    # 3. Validar credenciales críticas
    print_section("Validación de seguridad")
    
    validation = env_manager.validate_security_requirements()
    
    if validation['valid']:
        print("✅ Todas las variables críticas están configuradas")
    else:
        print("❌ Faltan variables críticas:")
        for var in validation['missing']:
            print(f"   ⚠️  {var}")
    
    if validation['warnings']:
        print("\n⚠️  Advertencias:")
        for warning in validation['warnings']:
            print(f"   🟡 {warning}")
    
    if validation['recommendations']:
        print("\n💡 Recomendaciones:")
        for rec in validation['recommendations']:
            print(f"   🔍 {rec}")
    
    # 4. Verificar credenciales de desarrollo
    print_section("Credenciales de desarrollo")
    
    try:
        dev_creds = env_manager.get_dev_credentials()
        print(f"👤 Usuario dev: {dev_creds.get('user', 'No configurado')}")
        print(f"🔑 Password configurada: {'✅ Sí' if dev_creds.get('password') else '❌ No'}")
        print(f"🚪 Auto-login: {'✅ Habilitado' if dev_creds.get('auto_login') else '❌ Deshabilitado'}")
        
        if dev_creds.get('auto_login') and is_prod:
            print("   ⚠️  ADVERTENCIA: Auto-login habilitado en producción")
    except Exception as e:
        print(f"❌ Error obteniendo credenciales de desarrollo: {e}")
    
    # 5. Verificar credenciales de base de datos
    print_section("Credenciales de base de datos")
    
    try:
        db_creds = env_manager.get_database_credentials()
        print(f"🖥️  Servidor: {db_creds.get('server', 'No configurado')}")
        print(f"👤 Usuario BD: {db_creds.get('username', 'No configurado')}")
        print(f"🔑 Password BD: {'✅ Configurada' if db_creds.get('password') else '❌ No configurada'}")
        print(f"📊 BD Inventario: {db_creds.get('inventario', 'No configurado')}")
        print(f"👥 BD Usuarios: {db_creds.get('users', 'No configurado')}")
        print(f"📋 BD Auditoría: {db_creds.get('auditoria', 'No configurado')}")
    except Exception as e:
        print(f"❌ Error obteniendo credenciales de BD: {e}")
    
    # 6. Verificar credenciales demo
    print_section("Credenciales de modo demo")
    
    try:
        demo_creds = env_manager.get_demo_credentials()
        for role, password in demo_creds.items():
            status = "✅ Configurada" if password else "❌ No configurada"
            print(f"🎭 {role.capitalize()}: {status}")
    except Exception as e:
        print(f"❌ Error obteniendo credenciales demo: {e}")
    
    # 7. Verificar configuración de seguridad
    print_section("Configuración de seguridad avanzada")
    
    try:
        security_config = env_manager.get_security_config()
        print(f"🔐 JWT Secret: {'✅ Configurada' if security_config.get('jwt_secret') else '❌ No configurada'}")
        print(f"🧂 Password Salt: {'✅ Configurada' if security_config.get('password_salt') else '❌ No configurada'}")
        print(f"🐛 Debug: {'✅ Habilitado' if security_config.get('debug') else '❌ Deshabilitado'}")
    except Exception as e:
        print(f"❌ Error obteniendo configuración de seguridad: {e}")
    
    # 8. Resumen final
    print_section("Resumen y recomendaciones finales")
    
    if validation['valid'] and not validation['warnings']:
        print("🎉 Configuración de seguridad: ✅ EXCELENTE")
        security_score = 100
    elif validation['valid'] and validation['warnings']:
        print("✅ Configuración de seguridad: 🟡 BUENA (con advertencias)")
        security_score = 80
    elif not validation['valid'] and len(validation['missing']) <= 2:
        print("⚠️  Configuración de seguridad: 🟠 REGULAR (faltan variables)")
        security_score = 60
    else:
        print("❌ Configuración de seguridad: 🔴 DEFICIENTE (múltiples problemas)")
        security_score = 40
    
    print(f"📊 Puntuación de seguridad: {security_score}/100")
    
    # Consejos específicos
    print("\n💡 Pasos siguientes:")
    
    if not env_file.exists():
        print("   1. 📋 Copiar .env.example como .env")
        print("   2. ✏️  Configurar todas las variables necesarias")
    
    if validation['missing']:
        print("   3. 🔧 Configurar variables críticas faltantes")
    
    if is_dev and not os.getenv('REXUS_DEV_PASSWORD'):
        print("   4. 🔑 Configurar REXUS_DEV_PASSWORD para desarrollo")
    
    print("   5. 🔒 Verificar que .env esté en .gitignore")
    print("   6. 🧪 Ejecutar tests de seguridad")
    
    print_separator()
    
    return validation['valid']


if __name__ == "__main__":
    success = validate_environment()
    sys.exit(0 if success else 1)