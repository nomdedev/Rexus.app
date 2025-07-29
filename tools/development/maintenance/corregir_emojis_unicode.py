#!/usr/bin/env python3
"""
Script para corregir emojis Unicode que causan problemas de codificación en consola.
"""

from pathlib import Path


def corregir_emojis_en_archivo(ruta_archivo):
    """Corrige los emojis Unicode en un archivo específico."""
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()

        contenido_original = contenido

        # Reemplazos de emojis comunes
        reemplazos = {
            "✅": "[OK]",
            "❌": "[ERROR]",
            "⚠️": "[WARN]",
            "🔧": "[TOOL]",
            "✓": "[OK]",
            "✗": "[ERROR]",
            "⭐": "[STAR]",
            "🎯": "[TARGET]",
            "📊": "[CHART]",
            "📝": "[NOTE]",
            "🚀": "[ROCKET]",
            "💡": "[IDEA]",
        }

        for emoji, reemplazo in reemplazos.items():
            contenido = contenido.replace(emoji, reemplazo)

        # Si hubo cambios, escribir el archivo
        if contenido != contenido_original:
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                f.write(contenido)
            return True

        return False
    except Exception as e:
        print(f"[ERROR] Error procesando {ruta_archivo}: {e}")
        return False


def main():
    """Función principal."""
    print("[TOOL] Iniciando corrección de emojis Unicode...")

    # Archivos a procesar (solo los críticos para la aplicación)
    archivos_criticos = [
        "main.py",
        "core/logger.py",
        "core/database.py",
        "modules/*/controller.py",
        "modules/*/model.py",
        "widgets/sistema_notificaciones.py",
    ]

    base_path = Path(__file__).parent.parent.parent
    archivos_corregidos = 0

    for patron in archivos_criticos:
        if "*" in patron:
            # Buscar archivos usando glob
            for archivo in base_path.glob(patron):
                if archivo.is_file() and archivo.suffix == ".py":
                    if corregir_emojis_en_archivo(archivo):
                        print(f"[OK] Corregido: {archivo.relative_to(base_path)}")
                        archivos_corregidos += 1
        else:
            # Archivo específico
            archivo = base_path / patron
            if archivo.exists() and archivo.is_file():
                if corregir_emojis_en_archivo(archivo):
                    print(f"[OK] Corregido: {archivo.relative_to(base_path)}")
                    archivos_corregidos += 1

    print(f"[OK] Corrección completada. {archivos_corregidos} archivos modificados.")


if __name__ == "__main__":
    main()
