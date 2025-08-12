#!/usr/bin/env python3
"""
Script simplificado para mejora de feedback visual en módulos Rexus
================================================================
"""

import os
import shutil
from pathlib import Path


def mejorar_feedback_modulos():
    """Mejora el feedback visual en módulos que lo necesiten."""
    print("🎨 MEJORANDO FEEDBACK VISUAL - MÓDULOS REXUS")
    print("=" * 55)

    modulos_dir = Path("rexus/modules")
    if not modulos_dir.exists():
        print("[ERROR] Error: Directorio rexus/modules no encontrado")
        return

    modulos_mejorados = []
    modulos_analizados = []

    # Analizar cada módulo
    for modulo_path in modulos_dir.iterdir():
        if modulo_path.is_dir() and not modulo_path.name.startswith("."):
            modulo_name = modulo_path.name
            view_file = modulo_path / "view.py"

            print(f"🔍 Analizando módulo: {modulo_name}")
            modulos_analizados.append(modulo_name)

            if view_file.exists():
                needs_improvement = analizar_view_file(view_file)
                if needs_improvement:
                    print(f"[WARN] {modulo_name} necesita mejoras de feedback visual")
                    if aplicar_mejoras_basicas(view_file, modulo_name):
                        modulos_mejorados.append(modulo_name)
                        print(f"[CHECK] {modulo_name} mejorado")
                else:
                    print(f"[CHECK] {modulo_name} ya tiene buen feedback visual")
            else:
                print(f"[WARN] {modulo_name}: view.py no encontrado")

    # Reporte final
    print("\n" + "=" * 55)
    print(f"[CHART] REPORTE FINAL:")
    print(f"   📋 Módulos analizados: {len(modulos_analizados)}")
    print(f"   [CHECK] Módulos mejorados: {len(modulos_mejorados)}")
    print(
        f"   📝 Módulos que ya tenían buen feedback: {len(modulos_analizados) - len(modulos_mejorados)}"
    )

    if modulos_mejorados:
        print(f"\n🎉 MÓDULOS MEJORADOS:")
        for modulo in modulos_mejorados:
            print(f"   - {modulo}")

        # Crear reporte
        crear_reporte_mejoras(modulos_analizados, modulos_mejorados)

    print("\n🔧 PRÓXIMOS PASOS:")
    print("   1. Ejecutar aplicación para probar mejoras")
    print("   2. Revisar y ajustar estilos si es necesario")
    print("   3. Ejecutar tests de funcionalidad")


def analizar_view_file(view_file: Path) -> bool:
    """Analiza si un archivo view.py necesita mejoras de feedback."""
    try:
        with open(view_file, "r", encoding="utf-8") as f:
            contenido = f.read()

        # Buscar indicadores de feedback actual
        indicadores_feedback = [
            "QMessageBox",
            "statusBar",
            "setCursor.*Wait",
            "loading",
            "progress",
            "feedback",
            "show_message",
            "show_error",
        ]

        feedback_encontrado = 0
        for indicador in indicadores_feedback:
            if indicador.lower() in contenido.lower():
                feedback_encontrado += 1

        # Si tiene menos de 2 indicadores de feedback, necesita mejoras
        return feedback_encontrado < 2

    except Exception as e:
        print(f"   [ERROR] Error leyendo {view_file}: {e}")
        return False


def aplicar_mejoras_basicas(view_file: Path, modulo_name: str) -> bool:
    """Aplica mejoras básicas de feedback visual."""
    try:
        # Crear backup
        backup_dir = Path("backups_feedback")
        backup_dir.mkdir(exist_ok=True)
        backup_file = backup_dir / f"{modulo_name}_view_backup.py"
        shutil.copy2(view_file, backup_file)

        with open(view_file, "r", encoding="utf-8") as f:
            contenido = f.read()

        # Buscar si ya tiene imports necesarios
        mejoras_aplicadas = False

        # Agregar import de QMessageBox si no está
        if (
            "QMessageBox" not in contenido
            and "from PyQt6.QtWidgets import" in contenido
        ):
            contenido = contenido.replace(
                "from PyQt6.QtWidgets import",
                "from PyQt6.QtWidgets import QMessageBox,",
            )
            mejoras_aplicadas = True

        # Agregar método de feedback básico si no existe
        if "def mostrar_mensaje" not in contenido and "class " in contenido:
            feedback_method = '''
    def mostrar_mensaje(self, mensaje: str, tipo: str = "info"):
        """Muestra mensaje de feedback al usuario."""
        if tipo == "error":
            QMessageBox.critical(self, "Error", mensaje)
        elif tipo == "success":
            QMessageBox.information(self, "Éxito", mensaje)
        elif tipo == "warning":
            QMessageBox.warning(self, "Advertencia", mensaje)
        else:
            QMessageBox.information(self, "Información", mensaje)
'''

            # Buscar el final de la clase principal
            lines = contenido.split("\n")
            insert_pos = -1
            for i, line in enumerate(lines):
                if line.strip().startswith("class ") and "View" in line:
                    # Buscar el final de esta clase
                    for j in range(i + 1, len(lines)):
                        if (
                            lines[j]
                            and not lines[j].startswith(" ")
                            and not lines[j].startswith("\t")
                        ):
                            insert_pos = j
                            break
                    break

            if insert_pos > 0:
                lines.insert(insert_pos, feedback_method)
                contenido = "\n".join(lines)
                mejoras_aplicadas = True

        # Guardar si se aplicaron mejoras
        if mejoras_aplicadas:
            with open(view_file, "w", encoding="utf-8") as f:
                f.write(contenido)
            return True

        return False

    except Exception as e:
        print(f"   [ERROR] Error aplicando mejoras a {modulo_name}: {e}")
        return False


def crear_reporte_mejoras(analizados: list, mejorados: list):
    """Crea un reporte de las mejoras aplicadas."""
    reporte = f"""# Reporte de Mejoras de Feedback Visual - Rexus.app

**Fecha:** {Path(__file__).stat().st_mtime}
**Módulos analizados:** {len(analizados)}
**Módulos mejorados:** {len(mejorados)}

## Módulos Analizados
{chr(10).join(f"- {modulo}" for modulo in analizados)}

## Módulos Mejorados
{chr(10).join(f"- [CHECK] {modulo}" for modulo in mejorados)}

## Mejoras Aplicadas

### 1. Imports de QMessageBox
- Agregado import automático cuando faltaba

### 2. Método mostrar_mensaje()
- Método estándar para feedback de usuario
- Soporte para diferentes tipos: info, success, warning, error
- Integración con QMessageBox nativo

### 3. Backups Creados
- Backup automático en `backups_feedback/` antes de modificar
- Permite restaurar versión original si es necesario

## Próximos Pasos

1. **Probar mejoras** - Ejecutar aplicación y verificar feedback
2. **Integrar con temas** - Asegurar que siga estilos del tema global
3. **Agregar más feedback** - Spinners, progress bars, etc.
4. **Tests de UX** - Validar experiencia de usuario

## Archivos de Backup
{chr(10).join(f"- backups_feedback/{modulo}_view_backup.py" for modulo in mejorados)}

---
*Reporte generado automáticamente por script de mejoras*
"""

    with open("mejoras_feedback_visual.md", "w", encoding="utf-8") as f:
        f.write(reporte)

    print("   📋 Reporte guardado en: mejoras_feedback_visual.md")


if __name__ == "__main__":
    mejorar_feedback_modulos()
