#!/usr/bin/env python3
"""
Script de Validación Automática de Sintaxis - Rexus App
Valida la sintaxis de todos los módulos críticos
"""

import ast
import os
import sys
from pathlib import Path

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def validar_sintaxis_archivo(ruta_archivo):
    """Valida la sintaxis de un archivo Python."""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            codigo = f.read()

        # Intentar parsear el código
        ast.parse(codigo)
        return True, None

    except SyntaxError as e:
        return False, f"Línea {e.lineno}: {e.msg}"
    except FileNotFoundError:
        return False, "Archivo no encontrado"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"

def obtener_archivos_modulos():
    """Obtiene la lista de todos los archivos de módulos a validar."""
    base_path = Path("rexus/modules")

    archivos_criticos = [
        # Controllers
        base_path / "inventario" / "controller.py",
        base_path / "obras" / "controller.py",
        base_path / "administracion" / "controller.py",
        base_path / "pedidos" / "controller.py",
        base_path / "configuracion" / "controller.py",
        base_path / "auditoria" / "controller.py",
        base_path / "vidrios" / "controller.py",
        base_path / "logistica" / "controller.py",
        base_path / "mantenimiento" / "controller.py",
        base_path / "usuarios" / "controller.py",
        base_path / "compras" / "controller.py",

        # Models
        base_path / "inventario" / "model.py",
        base_path / "obras" / "model.py",
        base_path / "administracion" / "model.py",
        base_path / "pedidos" / "model.py",
        base_path / "configuracion" / "model.py",
        base_path / "auditoria" / "model.py",
        base_path / "vidrios" / "model.py",
        base_path / "logistica" / "model.py",
        base_path / "mantenimiento" / "model.py",
        base_path / "usuarios" / "model.py",
        base_path / "compras" / "model.py",

        # Views
        base_path / "inventario" / "view.py",
        base_path / "obras" / "view.py",
        base_path / "administracion" / "view.py",
        base_path / "pedidos" / "view.py",
        base_path / "configuracion" / "view.py",
        base_path / "auditoria" / "view.py",
        base_path / "vidrios" / "view.py",
        base_path / "logistica" / "view.py",
        base_path / "mantenimiento" / "view.py",
        base_path / "usuarios" / "view.py",
        base_path / "compras" / "view.py",
    ]

    return [str(archivo) for archivo in archivos_criticos if archivo.exists()]

def validar_todos_los_modulos():
    """Valida todos los módulos y genera reporte."""
    print(f"{Colors.BOLD}{Colors.BLUE}🔍 VALIDADOR DE SINTAXIS - REXUS APP{Colors.END}")
    print("=" * 60)

    archivos = obtener_archivos_modulos()
    errores_encontrados = []
    archivos_validos = 0

    print(f"\n📋 Validando {len(archivos)} archivos...\n")

    for archivo in archivos:
        valido, error = validar_sintaxis_archivo(archivo)

        # Mostrar resultado
        if valido:
            print(f"{Colors.GREEN}[CHECK]{Colors.END} {archivo}")
            archivos_validos += 1
        else:
            print(f"{Colors.RED}[ERROR]{Colors.END} {archivo}")
            print(f"   {Colors.RED}→ {error}{Colors.END}")
            errores_encontrados.append((archivo, error))

    # Resumen
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}[CHART] RESUMEN DE VALIDACIÓN{Colors.END}")
    print(f"[CHECK] Archivos válidos: {Colors.GREEN}{archivos_validos}{Colors.END}")
    print(f"[ERROR] Archivos con errores: {Colors.RED}{len(errores_encontrados)}{Colors.END}")
    print(f"📁 Total archivos: {len(archivos)}")

    # Porcentaje de éxito
    porcentaje = (archivos_validos / len(archivos)) * 100 if archivos else 0
    color = Colors.GREEN if porcentaje == 100 else Colors.YELLOW if porcentaje >= 75 else Colors.RED
    print(f"📈 Porcentaje de éxito: {color}{porcentaje:.1f}%{Colors.END}")

    # Detalles de errores
    if errores_encontrados:
        print(f"\n{Colors.BOLD}{Colors.RED}🚨 ERRORES ENCONTRADOS:{Colors.END}")
        print("-" * 40)

        for i, (archivo, error) in enumerate(errores_encontrados, 1):
            print(f"{i}. {archivo}")
            print(f"   Error: {error}")
            print()

    # Archivos críticos con errores
    archivos_criticos_con_errores = [
        archivo for archivo, _ in errores_encontrados
        if "controller.py" in archivo
    ]

    if archivos_criticos_con_errores:
        print(f"{Colors.BOLD}{Colors.RED}[WARN]  CONTROLADORES BLOQUEADOS:{Colors.END}")
        for archivo in archivos_criticos_con_errores:
            modulo = archivo.split("/")[-2] if "/" in archivo else archivo.split("\\")[-2]
            print(f"   • {modulo}")
        print()

    # Recomendaciones
    print(f"{Colors.BOLD}{Colors.BLUE}💡 PRÓXIMOS PASOS:{Colors.END}")
    if errores_encontrados:
        print("1. Corregir errores de sintaxis críticos")
        print("2. Ejecutar nuevamente este script para validar")
        print("3. Continuar con el plan de corrección completo")
        return False
    else:
        print("[CHECK] ¡Todos los archivos tienen sintaxis válida!")
        print("[CHECK] Continuar con las siguientes fases del plan")
        return True

def generar_script_correccion():
    """Genera un script de corrección automática para patrones comunes."""
    script_content = '''#!/usr/bin/env python3
"""
Script de Corrección Automática de Patrones Comunes
USAR CON PRECAUCIÓN - Crear backup antes de ejecutar
"""

import re
import os
import shutil
from datetime import datetime

def crear_backup(archivo):
    """Crea backup del archivo antes de modificar."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{archivo}.backup_{timestamp}"
    shutil.copy2(archivo, backup_file)
    return backup_file

def corregir_docstrings_mal_indentados(archivo):
    """Corrige docstrings con patrón ):\"\"\" incorrectos."""
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()

    contenido_original = contenido

    # Patrón 1: ):"""""" → ):\\n        """"""""
    patron1 = r'(\\):)("""[^"]*""")'
    reemplazo1 = r'\\1\\n        \\2'
    contenido = re.sub(patron1, reemplazo1, contenido)

    # Patrón 2: Indentación incorrecta después de métodos
    patron2 = r'(def \\w+\\([^)]*\\):)(""")'
    reemplazo2 = r'\\1\\n        \\2'
    contenido = re.sub(patron2, reemplazo2, contenido)

    if contenido != contenido_original:
        # Crear backup
        backup = crear_backup(archivo)
        print(f"📄 Backup creado: {backup}")

        # Escribir contenido corregido
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)

        return True

    return False

# Lista de archivos a corregir
archivos_a_corregir = [
    "rexus/modules/inventario/controller.py",
    "rexus/modules/obras/controller.py",
    "rexus/modules/administracion/controller.py",
    # Agregar más según necesidad
]

if __name__ == "__main__":
    print("🔧 CORRECTOR AUTOMÁTICO DE PATRONES")
    print("[WARN]  ESTO MODIFICARÁ LOS ARCHIVOS - Se crearán backups")

    respuesta = input("¿Continuar? (s/N): ")
    if respuesta.lower() != 's':
        print("Operación cancelada")
        exit()

    for archivo in archivos_a_corregir:
        if os.path.exists(archivo):
            if corregir_docstrings_mal_indentados(archivo):
                print(f"[CHECK] Corregido: {archivo}")
            else:
                print(f"ℹ️  Sin cambios: {archivo}")
        else:
            print(f"[ERROR] No encontrado: {archivo}")
'''

    with open("scripts/corregir_patrones.py", "w", encoding="utf-8") as f:
        f.write(script_content)

    print(f"\n{Colors.BLUE}📝 Script de corrección generado: scripts/corregir_patrones.py{Colors.END}")

if __name__ == "__main__":
    # Crear directorio scripts si no existe
    os.makedirs("scripts", exist_ok=True)

    # Ejecutar validación
    todos_validos = validar_todos_los_modulos()

    # Generar script de corrección si hay errores
    if not todos_validos:
        generar_script_correccion()

    # Código de salida
    sys.exit(0 if todos_validos else 1)
