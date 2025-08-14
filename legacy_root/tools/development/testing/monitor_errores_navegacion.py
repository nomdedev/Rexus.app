#!/usr/bin/env python3
"""
Monitor de errores en tiempo real para detectar problemas durante la navegación manual.
"""

def monitor_logs():
    """Monitorea los logs en tiempo real"""

    # Archivos de log a monitorear
    log_files = [
        'logs/app.log',
        'logs/app_json.log',
        'logs/error_inicio_ui.txt'
    ]

    # Estado inicial de los archivos
    file_states = {}

    for log_file in log_files:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                file_states[log_file] = len(f.readlines())
        else:
            file_states[log_file] = 0

    print("🔍 Monitor de errores iniciado. Navegue por la aplicación para detectar errores...")
    print("Presione Ctrl+C para detener el monitoreo.\n")

    errores_detectados = []

    try:
        while True:
            for log_file in log_files:
                if os.path.exists(log_file):
                    with open(log_file,
'r',
                        encoding='utf-8',
                        errors='ignore') as f:
                        lines = f.readlines()
                        current_line_count = len(lines)

                        # Si hay nuevas líneas
                        if current_line_count > file_states[log_file]:
                            new_lines = lines[file_states[log_file]:]

                            for line in new_lines:
                                line = line.strip()
                                if not line:
                                    continue

                                # Detectar errores y warnings importantes
                                is_error = any(keyword in line.lower() for keyword in [
                                    'error', 'exception', 'traceback', 'failed', 'critical',
                                    'qpixmap', 'stylesheet', 'warning', 'could not load'
                                ])

                                if is_error:
                                    timestamp = datetime.now().strftime('%H:%M:%S')
                                    error_info = {
                                        'timestamp': timestamp,
                                        'file': log_file,
                                        'message': line
                                    }
                                    errores_detectados.append(error_info)

                                    # Mostrar el error en tiempo real
                                    print(f"🚨 [{timestamp}] {log_file}")
                                    print(f"   {line}")
                                    print()

                            file_states[log_file] = current_line_count

            time.sleep(1)  # Revisar cada segundo

    except KeyboardInterrupt:
        print("\n" + "="*60)
        print("[CHART] RESUMEN DE ERRORES DETECTADOS")
        print("="*60)

        if errores_detectados:
            print(f"[ERROR] Total de errores/warnings detectados: {len(errores_detectados)}")
            print("\nDesglose por archivo:")

            file_counts = {}
            for error in errores_detectados:
                file_name = error['file']
                file_counts[file_name] = file_counts.get(file_name, 0) + 1

            for file_name, count in file_counts.items():
                print(f"  📄 {file_name}: {count} errores")

            print("\nÚltimos 10 errores:")
            for error in errores_detectados[-10:]:
                print(f"  🕒 {error['timestamp']} - {error['file']}")
                print(f"     {error['message'][:100]}...")

            # Guardar reporte detallado
            try:
                os.makedirs('tests/reports', exist_ok=True)
                reporte = {
                    'fecha': datetime.now().isoformat(),
                    'total_errores': len(errores_detectados),
                    'errores_por_archivo': file_counts,
                    'errores_detallados': errores_detectados
                }

                with open('tests/reports/monitor_errores_navegacion.json', 'w', encoding='utf-8') as f:
                    json.dump(reporte, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Reporte guardado en: tests/reports/monitor_errores_navegacion.json")
            except Exception as e:
                print(f"[WARN] Error al guardar reporte: {e}")

        else:
            print("🎉 ¡No se detectaron errores durante la navegación!")

        print("\n✨ Monitor finalizado")

def check_app_running():
    """Verifica si la aplicación está ejecutándose"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('main.py' in arg for arg in cmdline):
                    return True
import json
import os
import time
from datetime import datetime

import psutil

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except ImportError:
        # Si psutil no está disponible, asumir que la app está corriendo
        return True
    return False

def main():
    """Función principal"""
    print("🔍 Monitor de errores en tiempo real")
    print("="*50)

    # Verificar si la aplicación está ejecutándose
    if not check_app_running():
        print("[WARN] No se detectó la aplicación ejecutándose.")
        print("💡 Asegúrese de que main.py esté ejecutándose antes de usar este monitor.")
        input("Presione Enter cuando haya iniciado la aplicación...")

    # Verificar que existen archivos de log
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        print(f"[ERROR] Directorio de logs no encontrado: {log_dir}")
        return

    print("📁 Monitoreando archivos de log:")
    log_files = ['app.log', 'app_json.log', 'error_inicio_ui.txt']
    for log_file in log_files:
        path = os.path.join(log_dir, log_file)
        status = "[CHECK]" if os.path.exists(path) else "[ERROR]"
        print(f"  {status} {path}")

    print("\n[ROCKET] Iniciando monitoreo...")
    monitor_logs()

if __name__ == '__main__':
    main()
