"""
Utilidades para correcciones críticas de tema
Soluciona problemas de formularios negros con tema oscuro

Fecha: 13/08/2025
Problema resuelto: QLineEdit, QTextEdit, QComboBox ilegibles con tema oscuro
"""

from PyQt6.QtWidgets import QWidget


def apply_critical_form_fixes(widget: QWidget = None):
    """
    Función de utilidad para aplicar correcciones críticas de formularios.
    Puede ser llamada desde cualquier módulo.

    Args:
        widget: Widget específico o None para aplicar globalmente
    """
    try:
        from rexus.ui.style_manager import StyleManager

        style_manager = StyleManager()
        success = style_manager.apply_critical_contrast_fixes(widget)

        if success:
            print("[THEME_FIX] Correcciones críticas aplicadas correctamente")
        else:
            print("[THEME_FIX] Error aplicando correcciones críticas")

        return success

    except Exception as e:
        print(f"[THEME_FIX] Error: {e}")
        return False


def ensure_forms_readable():
    """
    Garantiza que todos los formularios sean legibles.
    Aplica correcciones críticas automáticamente si es necesario.
    """
    try:
        # Aplicar correcciones globalmente
        return apply_critical_form_fixes()

    except Exception as e:
        print(f"[THEME_FIX] Error garantizando legibilidad: {e}")
        return False


def fix_dark_theme_forms():
    """
    Método específico para corregir formularios en tema oscuro.
    Alias para compatibilidad con código existente.
    """
    print("[THEME_FIX] Aplicando correcciones para tema oscuro...")
    return ensure_forms_readable()


def get_safe_dark_styles():
    """
    Retorna estilos seguros para tema oscuro que garantizan legibilidad.

    Returns:
        str: CSS seguro para tema oscuro
    """
    return """
    /* Estilos seguros para tema oscuro - garantiza legibilidad */
    QLineEdit, QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit {
        background-color: #1e293b !important;
        border: 2px solid #475569 !important;
        border-radius: 6px !important;
        color: #f1f5f9 !important;
        font-size: 14px !important;
        padding: 8px 12px !important;
    }

    QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
        background-color: #334155 !important;
        border: 2px solid #60a5fa !important;
        color: #ffffff !important;
    }

    QPushButton {
        background-color: #1e40af !important;
        color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 6px !important;
        min-height: 32px !important;
        padding: 8px 16px !important;
    }

    QLabel {
        color: #e2e8f0 !important;
    }
    """


def apply_safe_dark_styles(widget: QWidget):
    """
    Aplica estilos seguros para tema oscuro a un widget específico.

    Args:
        widget: Widget al que aplicar estilos seguros
    """
    try:
        if widget:
            safe_styles = get_safe_dark_styles()
            current_style = widget.styleSheet()
            widget.setStyleSheet(current_style + safe_styles)
            print(f"[THEME_FIX] Estilos seguros aplicados a {widget.__class__.__name__}")
            return True
        return False

    except Exception as e:
        print(f"[THEME_FIX] Error aplicando estilos seguros: {e}")
        return False


def is_dark_theme_active():
    """
    Detecta si actualmente hay un tema oscuro activo.

    Returns:
        bool: True si tema oscuro está activo
    """
    try:
        from rexus.ui.style_manager import StyleManager

        style_manager = StyleManager()
        current_theme = getattr(style_manager, '_current_theme', 'light')

        return 'dark' in current_theme.lower()

    except Exception:
        return False


# Función de conveniencia para usar en módulos
def ensure_module_forms_readable(module_widget: QWidget):
    """
    Función de conveniencia para usar en cualquier módulo.
    Garantiza que los formularios del módulo sean legibles.

    Args:
        module_widget: Widget principal del módulo

    Usage:
        from rexus.utils.theme_fixes import ensure_module_forms_readable

        class MiModuloView(QWidget):
            def __init__(self):
                super().__init__()
                self.setup_ui()
                # Garantizar legibilidad después de crear UI
                ensure_module_forms_readable(self)
    """
    try:
        if is_dark_theme_active():
            print(f"[THEME_FIX] Tema oscuro detectado - aplicando correcciones a módulo")
            return apply_safe_dark_styles(module_widget)
        return True

    except Exception as e:
        print(f"[THEME_FIX] Error en correcciones de módulo: {e}")
        return False
