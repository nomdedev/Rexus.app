#!/usr/bin/env python3
"""
MIT License - Copyright (c) 2025 Rexus.app

Admin Rate Limiter - Rexus.app
==============================

Herramienta administrativa para gestionar el sistema de rate limiting:
- Ver usuarios bloqueados
- Resetear intentos de usuarios
- Ver estadísticas globales
- Configurar parámetros
"""

import sys
from pathlib import Path
import datetime

# Agregar ruta del proyecto
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from rexus.core.rate_limiter import get_rate_limiter, RateLimitConfig, initialize_rate_limiter
    RATE_LIMITER_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Rate limiter no disponible: {e}")
    RATE_LIMITER_AVAILABLE = False


class RateLimiterAdmin:
    """Herramienta administrativa para rate limiter"""

    def __init__(self):
        if not RATE_LIMITER_AVAILABLE:
            print("[ERROR] [ERROR] Rate limiter no disponible")
            sys.exit(1)

        self.rate_limiter = get_rate_limiter()

    def show_menu(self):
        """Muestra el menú principal"""
        print("\n" + "="*60)
        print("[ADMIN] Rate Limiter - Administración")
        print("="*60)
        print("1. Ver estadísticas generales")
        print("2. Listar usuarios bloqueados")
        print("3. Ver información de usuario específico")
        print("4. Resetear intentos de usuario")
        print("5. Ver configuración actual")
        print("6. Limpiar registros antiguos")
        print("0. Salir")
        print("-"*60)

        try:
            choice = input("Seleccione opción [0-6]: ").strip()
            return choice
        except KeyboardInterrupt:
            print("\n[INFO] Operación cancelada")
            return "0"

    def show_statistics(self):
        """Muestra estadísticas generales"""
        print("\n" + "="*50)
        print("[STATS] Estadísticas del Rate Limiter")
        print("="*50)

        stats = self.rate_limiter.get_statistics()

        print(f"[CHART] RESUMEN GENERAL:")
        print(f"   Usuarios rastreados: {stats['total_tracked_users']}")
        print(f"   Usuarios bloqueados: {stats['currently_blocked']}")
        print(f"   Intentos recientes (1h): {stats['recent_attempts_1h']}")

        print(f"\n⚙️  CONFIGURACIÓN ACTUAL:")
        print(f"   Máximo intentos: {stats['config']['max_attempts']}")
        print(f"   Bloqueo base: {stats['config']['base_lockout_minutes']} minutos")
        print(f"   Bloqueo máximo: {stats['config']['max_lockout_minutes']} minutos")

        # Mostrar actividad reciente si hay
        if stats['recent_attempts_1h'] > 0:
            print(f"\n[WARN]  ALERTA: {stats['recent_attempts_1h']} intentos en la última hora")
            print(f"           Posible actividad de fuerza bruta")

    def list_blocked_users(self):
        """Lista usuarios actualmente bloqueados"""
        print("\n" + "="*50)
        print("[BLOCKED] Usuarios Bloqueados")
        print("="*50)

        now = datetime.datetime.now()
        blocked_users = []

        for username, data in self.rate_limiter.attempts.items():
            locked_until = data.get('locked_until')
            if locked_until and locked_until > now:
                remaining_time = locked_until - now
                minutes_remaining = int(remaining_time.total_seconds() / 60)

                blocked_users.append({
                    'username': username,
                    'failures': data.get('consecutive_failures', 0),
                    'locked_until': locked_until,
                    'minutes_remaining': minutes_remaining
                })

        if not blocked_users:
            print("[CHECK] No hay usuarios bloqueados actualmente")
            return

        print(f"[LOCK] USUARIOS BLOQUEADOS ({len(blocked_users)}):")
        print(f"   {'Usuario':<20} {'Fallos':<8} {'Tiempo Restante':<15} {'Bloqueado Hasta'}")
        print(f"   {'-'*20} {'-'*8} {'-'*15} {'-'*20}")

        for user in blocked_users:
            print(f"   {user['username']:<20} {user['failures']:<8} "
                  f"{user['minutes_remaining']} min{'':<10} "
                  f"{user['locked_until'].strftime('%H:%M:%S')}")

    def show_user_info(self):
        """Muestra información detallada de un usuario"""
        try:
            username = input("\nIngrese nombre de usuario: ").strip()
            if not username:
                print("[ERROR] Nombre de usuario requerido")
                return

            print(f"\n" + "="*50)
            print(f"[USER INFO] Información de '{username}'")
            print("="*50)

            info = self.rate_limiter.get_lockout_info(username)

            print(f"👤 USUARIO: {username}")
            print(f"   Estado: {'[LOCK] BLOQUEADO' if info['is_blocked'] else '[CHECK] ACTIVO'}")
            print(f"   Fallos consecutivos: {info['consecutive_failures']}")
            print(f"   Intentos restantes: {info['remaining_attempts']}")
            print(f"   Intentos recientes (1h): {info['recent_attempts']}")

            if info['is_blocked'] and info['locked_until']:
                remaining_time = info['locked_until'] - datetime.datetime.now()
                minutes_remaining = max(0, int(remaining_time.total_seconds() / 60))
                print(f"   Bloqueado hasta: {info['locked_until'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Tiempo restante: {minutes_remaining} minutos")

            # Mostrar historial de intentos si existe
            if username in self.rate_limiter.attempts:
                attempts = self.rate_limiter.attempts[username].get('attempts', [])
                if attempts:
                    print(f"\n📈 HISTORIAL RECIENTE ({len(attempts)} intentos):")
                    for i, attempt_time in enumerate(attempts[-5:], 1):  # Últimos 5
                        print(f"   {i}. {attempt_time.strftime('%H:%M:%S')}")

        except KeyboardInterrupt:
            print("\n[INFO] Operación cancelada")

    def reset_user_attempts(self):
        """Resetea los intentos de un usuario"""
        try:
            username = input("\nIngrese nombre de usuario a resetear: ").strip()
            if not username:
                print("[ERROR] Nombre de usuario requerido")
                return

            # Verificar si el usuario existe en el sistema
            if username not in self.rate_limiter.attempts:
                print(f"ℹ️  Usuario '{username}' no tiene registros de intentos fallidos")
                return

            # Confirmar acción
            info = self.rate_limiter.get_lockout_info(username)
            print(f"\n📋 INFORMACIÓN ACTUAL:")
            print(f"   Usuario: {username}")
            print(f"   Fallos consecutivos: {info['consecutive_failures']}")
            print(f"   Estado: {'[LOCK] BLOQUEADO' if info['is_blocked'] else '[CHECK] ACTIVO'}")

            confirm = input(f"\n¿Confirma resetear intentos de '{username}'? [y/N]: ").strip().lower()

            if confirm == 'y' or confirm == 'yes':
                # Obtener usuario admin (simulado)
                admin_user = input("Ingrese su usuario de admin: ").strip() or "admin"

                # Resetear intentos
                self.rate_limiter.reset_user_attempts(username, admin_user)

                print(f"[CHECK] Intentos de '{username}' reseteados exitosamente")
                print(f"   Acción registrada en auditoría por usuario: {admin_user}")
            else:
                print("[ERROR] Operación cancelada")

        except KeyboardInterrupt:
            print("\n[INFO] Operación cancelada")

    def show_config(self):
        """Muestra configuración actual"""
        print("\n" + "="*50)
        print("[CONFIG] Configuración del Rate Limiter")
        print("="*50)

        config = self.rate_limiter.config

        print(f"⚙️  PARÁMETROS DE SEGURIDAD:")
        print(f"   Máximo intentos permitidos: {config.max_attempts}")
        print(f"   Bloqueo base: {config.base_lockout_minutes} minutos")
        print(f"   Bloqueo máximo: {config.max_lockout_minutes} minutos")
        print(f"   Multiplicador progresivo: {config.progressive_multiplier}x")
        print(f"   Limpieza automática: {config.cleanup_hours} horas")

        print(f"\n[CHART] ESCALACIÓN DE BLOQUEOS:")
        print(f"   1er bloqueo: {config.base_lockout_minutes} min")
        print(f"   2do bloqueo: {config.base_lockout_minutes * config.progressive_multiplier} min")
        print(f"   3er bloqueo: {config.base_lockout_minutes * (config.progressive_multiplier ** 2)} min")
        print(f"   Máximo: {config.max_lockout_minutes} min")

        # Mostrar archivo de datos
        data_file = self.rate_limiter.data_file
        print(f"\n💾 PERSISTENCIA:")
        print(f"   Archivo de datos: {data_file}")
        print(f"   Existe: {'[CHECK] Sí' if data_file.exists() else '[ERROR] No'}")
        if data_file.exists():
            size_kb = data_file.stat().st_size / 1024
            print(f"   Tamaño: {size_kb:.1f} KB")

    def cleanup_old_records(self):
        """Limpia registros antiguos"""
        print("\n" + "="*50)
        print("[CLEANUP] Limpieza de Registros")
        print("="*50)

        before_count = len(self.rate_limiter.attempts)
        print(f"[CHART] Registros antes de limpieza: {before_count}")

        self.rate_limiter._cleanup_old_records()

        after_count = len(self.rate_limiter.attempts)
        cleaned = before_count - after_count

        print(f"[CHART] Registros después de limpieza: {after_count}")
        print(f"🧹 Registros eliminados: {cleaned}")

        if cleaned > 0:
            print(f"[CHECK] Limpieza completada - {cleaned} registros antiguos eliminados")
        else:
            print(f"ℹ️  No hay registros antiguos para limpiar")

    def run(self):
        """Ejecuta el sistema administrativo"""
        print("[ADMIN] Rate Limiter - Herramienta Administrativa")
        print("=" * 60)
        print("Herramienta para administrar el sistema de rate limiting")

        try:
            while True:
                choice = self.show_menu()

                if choice == "1":
                    self.show_statistics()
                elif choice == "2":
                    self.list_blocked_users()
                elif choice == "3":
                    self.show_user_info()
                elif choice == "4":
                    self.reset_user_attempts()
                elif choice == "5":
                    self.show_config()
                elif choice == "6":
                    self.cleanup_old_records()
                elif choice == "0":
                    print("\n👋 Saliendo del administrador de rate limiter")
                    break
                else:
                    print("[ERROR] Opción inválida. Seleccione 0-6")

                # Pausa para leer resultado
                if choice != "0":
                    input("\nPresione Enter para continuar...")

        except KeyboardInterrupt:
            print("\n\n👋 Administrador terminado por usuario")


def main():
    """Función principal"""
    try:
        admin = RateLimiterAdmin()
        admin.run()

    except Exception as e:
        print(f"[ERROR] Error ejecutando administrador: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
