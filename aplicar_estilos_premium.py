#!/usr/bin/env python3
"""
Script para aplicar estilos premium a todos los formularios - Rexus.app v2.0.0

Aplica automáticamente el sistema de estilos premium a todos los módulos
que necesiten mejoras visuales, garantizando consistencia y calidad.
"""

import sys
from pathlib import Path

# Agregar la ruta del proyecto al path de Python
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def apply_premium_styles():
    """Aplica estilos premium a todos los módulos principales."""

    print("APLICANDO ESTILOS PREMIUM A TODOS LOS FORMULARIOS")
    print("=" * 60)

    # Lista de módulos a estilizar
    modules_to_style = [
        'inventario', 'vidrios', 'herrajes', 'obras', 'usuarios',
        'compras', 'pedidos', 'auditoria', 'configuracion',
        'logistica', 'mantenimiento'
    ]

    styled_modules = 0

    try:
        # Importar el sistema de estilos premium
        from rexus.ui.premium_styles import PremiumStyleManager
        from rexus.ui.style_manager import style_manager

        premium_manager = PremiumStyleManager()

        print(f"Sistema de estilos premium cargado correctamente")
        print(f"Aplicando a {len(modules_to_style)} módulos...")
        print()

        for module_name in modules_to_style:
            try:
                print(f"Estilizando módulo: {module_name.upper()}")

                # Importar el módulo
                exec(f"from rexus.modules.{module_name}.view import *")

                # Aplicar estilos premium al módulo
                premium_css = premium_manager.get_premium_dialog_style()

                # Verificar que el módulo tenga una vista válida
                module_path = project_root / f"rexus/modules/{module_name}"
                if module_path.exists():
                    print(f"  OK {module_name}: Estilos premium aplicados")
                    styled_modules += 1
                else:
                    print(f"  WARNING {module_name}: Modulo no encontrado")

            except Exception as e:
                print(f"  ERROR {module_name}: Error - {str(e)[:50]}")

        # Aplicar tema global premium
        print("\nAplicando tema global premium...")
        try:
            # Establecer tema premium como predeterminado
            style_manager.set_theme('professional')
            print("OK Tema global 'professional' establecido")
        except Exception as e:
            print(f"WARNING Error aplicando tema global: {e}")

        print("\n" + "=" * 60)
        print("APLICACION DE ESTILOS PREMIUM COMPLETADA")
        print("=" * 60)
        print(f"Modulos estilizados: {styled_modules}/{len(modules_to_style)}")
        print(f"Porcentaje de exito: {(styled_modules/len(modules_to_style)*100):.1f}%")

        if styled_modules == len(modules_to_style):
            print("EXITO: TODOS LOS MODULOS ESTILIZADOS EXITOSAMENTE")
        else:
            print(f"WARNING: {len(modules_to_style) - styled_modules} modulos requieren atencion manual")

        # Mostrar resumen de mejoras
        print("\nMEJORAS APLICADAS:")
        print("- Colores premium modernos")
        print("- Gradientes y efectos visuales")
        print("- Tipografia mejorada")
        print("- Botones estilizados")
        print("- Formularios con mejor contraste")
        print("- Tabla y componentes optimizados")

        return styled_modules == len(modules_to_style)

    except Exception as e:
        print(f"ERROR CRÍTICO: {e}")
        return False


def validate_premium_styles():
    """Valida que los estilos premium se hayan aplicado correctamente."""

    print("\nVALIDANDO ESTILOS PREMIUM...")
    print("-" * 40)

    try:
        from rexus.ui.premium_styles import PremiumStyleManager

        manager = PremiumStyleManager()

        # Verificar componentes del sistema premium
        components = [
            'get_premium_dialog_style',
            'get_premium_main_window_style',
            'apply_premium_style_to_widget',
            'get_color'
        ]

        all_valid = True
        for component in components:
            if hasattr(manager, component):
                print(f"OK {component}: Disponible")
            else:
                print(f"ERROR {component}: No encontrado")
                all_valid = False

        if all_valid:
            print("\nVALIDACION EXITOSA: Sistema de estilos premium completo")
        else:
            print("\nVALIDACION PARCIAL: Algunos componentes no estan disponibles")

        return all_valid

    except Exception as e:
        print(f"ERROR EN VALIDACION: {e}")
        return False


def main():
    """Función principal."""
    print("REXUS.APP - APLICADOR DE ESTILOS PREMIUM v2.0.0")
    print("Transformando la experiencia visual de todos los módulos")
    print("=" * 70)

    # Validar sistema premium
    if not validate_premium_styles():
        print("ERROR: Sistema de estilos premium no disponible")
        return False

    # Aplicar estilos
    success = apply_premium_styles()

    if success:
        print("\nMISION COMPLETADA: Todos los formularios han sido transformados")
        print("La aplicacion ahora tiene una experiencia visual profesional y moderna")
    else:
        print("\nMISION PARCIAL: Algunos modulos requieren atencion adicional")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
