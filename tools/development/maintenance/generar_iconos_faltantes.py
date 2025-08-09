"""
Script para crear iconos SVG básicos que faltan en la aplicación.
Genera iconos simples y funcionales para resolver los errores de archivos no encontrados.
"""

# Añadir el directorio raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import os
import sys


def crear_icono_svg(nombre, svg_content, ruta_destino):
    """
    Crea un archivo SVG con el contenido proporcionado.
    """
    try:
        os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
        with open(ruta_destino, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"[CHECK] Creado: {ruta_destino}")
        return True
    except Exception as e:
        print(f"[ERROR] Error creando {ruta_destino}: {e}")
        return False


def generar_iconos_faltantes():
    """
    Genera todos los iconos SVG que faltan en la aplicación.
    """
    print("🎨 Generando iconos SVG faltantes...")

    # Directorio base del proyecto
    base_dir = os.path.dirname(os.path.dirname(__file__))

    # Definir iconos y su contenido SVG
    iconos = {
        # Iconos en resources/icons/
        "resources/icons/logistica.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
  <polyline points="9,22 9,12 15,12 15,22"/>
  <rect x="4" y="15" width="3" height="3"/>
  <rect x="17" y="15" width="3" height="3"/>
</svg>""",
        "resources/icons/refresh-cw.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <polyline points="23 4 23 10 17 10"/>
  <polyline points="1 20 1 14 7 14"/>
  <path d="m3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
</svg>""",
        "resources/icons/guardar-permisos.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
  <polyline points="17,21 17,13 7,13 7,21"/>
  <polyline points="7,3 7,8 15,8"/>
  <path d="m9 16 2 2 4-4"/>
</svg>""",
        # Iconos en modules/resources/icons/
        "modules/resources/icons/add-entrega.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <circle cx="12" cy="12" r="10"/>
  <line x1="12" y1="8" x2="12" y2="16"/>
  <line x1="8" y1="12" x2="16" y2="12"/>
  <path d="M8 21h8"/>
</svg>""",
        "modules/resources/icons/search-icon.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <circle cx="11" cy="11" r="8"/>
  <line x1="21" y1="21" x2="16.65" y2="16.65"/>
</svg>""",
        "modules/resources/icons/excel_icon.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
  <polyline points="14,2 14,8 20,8"/>
  <line x1="16" y1="13" x2="8" y2="21"/>
  <line x1="8" y1="13" x2="16" y2="21"/>
</svg>""",
        "modules/resources/icons/factura.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
  <polyline points="14,2 14,8 20,8"/>
  <line x1="16" y1="13" x2="8" y2="13"/>
  <line x1="16" y1="17" x2="8" y2="17"/>
  <polyline points="10,9 9,9 8,9"/>
</svg>""",
        # Iconos en img/
        "img/add-material.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
  <line x1="12" y1="8" x2="12" y2="16"/>
  <line x1="8" y1="12" x2="16" y2="12"/>
  <path d="M7 21h10"/>
</svg>""",
        "img/plus_icon.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <circle cx="12" cy="12" r="10"/>
  <line x1="12" y1="8" x2="12" y2="16"/>
  <line x1="8" y1="12" x2="16" y2="12"/>
</svg>""",
        "img/actualizar.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <polyline points="23 4 23 10 17 10"/>
  <polyline points="1 20 1 14 7 14"/>
  <path d="m3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
</svg>""",
        "img/estadistica.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <line x1="18" y1="20" x2="18" y2="10"/>
  <line x1="12" y1="20" x2="12" y2="4"/>
  <line x1="6" y1="20" x2="6" y2="14"/>
</svg>""",
        "img/pdf.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
  <polyline points="14,2 14,8 20,8"/>
  <line x1="16" y1="13" x2="8" y2="13"/>
  <line x1="16" y1="17" x2="8" y2="17"/>
  <polyline points="10,9 9,9 8,9"/>
  <text x="12" y="15" font-size="6" text-anchor="middle">PDF</text>
</svg>""",
    }

    iconos_creados = 0

    # Crear cada icono
    for ruta_relativa, contenido_svg in iconos.items():
        ruta_completa = os.path.join(base_dir, ruta_relativa)
        if crear_icono_svg(
            os.path.basename(ruta_relativa), contenido_svg, ruta_completa
        ):
            iconos_creados += 1

    print(f"\n[CHART] Resumen:")
    print(f"   • Iconos creados: {iconos_creados}/{len(iconos)}")
    print(f"[CHECK] Generación de iconos completada")


def main():
    """
    Función principal.
    """
    generar_iconos_faltantes()


if __name__ == "__main__":
    main()
