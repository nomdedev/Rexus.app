#!/usr/bin/env python3
"""
Aplicador Automático de Mejoras UI/UX para Rexus.app
Implementa correcciones automáticas basadas en estándares
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class UIUXFixer:
    """Aplicador automático de correcciones UI/UX"""

    def __init__(self):
        self.root_path = Path(__file__).parent.parent.parent
        self.modules_path = self.root_path / "rexus" / "modules"
        self.backups_path = self.root_path / "backups_uiux"
        self.backups_path.mkdir(exist_ok=True)

        # Estándares de diseño
        self.design_standards = {
            "colores_primarios": {
                "#999999": "#2E7D32",  # Verde primario
                "#CCCCCC": "#388E3C",  # Verde medio
                "#DDDDDD": "#4CAF50",  # Verde claro
                "#888888": "#1976D2",  # Azul primario
            },
            "fuente_estandar": "Arial",
            "tamaños_fuente": [8, 9, 10, 11, 12, 14, 16],
            "espaciado_estandar": [5, 10, 15, 20, 25],
            "margenes_estandar": [5, 10, 15, 20],
        }

        self.corrections_applied = []

    def crear_backup(self, archivo: Path) -> Path:
        """Crea backup del archivo antes de modificarlo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{archivo.stem}_{timestamp}{archivo.suffix}"
        backup_path = self.backups_path / backup_name

        shutil.copy2(archivo, backup_path)
        return backup_path

    def aplicar_mejoras_accesibilidad(self, view_file: Path, modulo: str) -> int:
        """Aplica mejoras automáticas de accesibilidad"""
        correcciones = 0

        # Crear backup
        backup_path = self.crear_backup(view_file)

        try:
            with open(view_file, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            modified_lines = []

            i = 0
            while i < len(lines):
                line = lines[i]
                modified_line = line

                # 1. Agregar setAccessibleName a QPushButton
                if (
                    "QPushButton(" in line
                    and "setAccessibleName"
                    not in content[content.find(line) : content.find(line) + 200]
                ):
                    # Buscar el nombre del botón
                    button_match = re.search(r"self\.(\w+)\s*=\s*QPushButton", line)
                    if button_match:
                        button_name = button_match.group(1)
                        # Agregar línea de accesibilidad después
                        modified_lines.append(line)
                        modified_lines.append(
                            f"        self.{button_name}.setAccessibleName('{self._generar_nombre_accesible(button_name)}')"
                        )
                        correcciones += 1
                        self.corrections_applied.append(
                            f"{modulo}: Agregado nombre accesible a {button_name}"
                        )
                        i += 1
                        continue

                # 2. Agregar setAccessibleName a QLineEdit
                if (
                    "QLineEdit(" in line
                    and "setAccessibleName"
                    not in content[content.find(line) : content.find(line) + 200]
                ):
                    input_match = re.search(r"self\.(\w+)\s*=\s*QLineEdit", line)
                    if input_match:
                        input_name = input_match.group(1)
                        modified_lines.append(line)
                        modified_lines.append(
                            f"        self.{input_name}.setAccessibleName('{self._generar_nombre_accesible(input_name)}')"
                        )
                        correcciones += 1
                        self.corrections_applied.append(
                            f"{modulo}: Agregado nombre accesible a {input_name}"
                        )
                        i += 1
                        continue

                # 3. Agregar setToolTip a elementos interactivos
                if (
                    "QPushButton(" in line or "QToolButton(" in line
                ) and "setToolTip" not in content[
                    content.find(line) : content.find(line) + 200
                ]:
                    button_match = re.search(r"self\.(\w+)\s*=\s*Q\w+Button", line)
                    if button_match:
                        button_name = button_match.group(1)
                        modified_lines.append(line)
                        modified_lines.append(
                            f"        self.{button_name}.setToolTip('{self._generar_tooltip(button_name)}')"
                        )
                        correcciones += 1
                        self.corrections_applied.append(
                            f"{modulo}: Agregado tooltip a {button_name}"
                        )
                        i += 1
                        continue

                # 4. Mejorar políticas de foco
                if "setFocusPolicy(Qt.NoFocus)" in line:
                    modified_line = line.replace("Qt.NoFocus", "Qt.TabFocus")
                    correcciones += 1
                    self.corrections_applied.append(
                        f"{modulo}: Mejorada política de foco"
                    )

                modified_lines.append(modified_line)
                i += 1

            # Guardar cambios si hubo modificaciones
            if correcciones > 0:
                new_content = "\n".join(modified_lines)
                with open(view_file, "w", encoding="utf-8") as f:
                    f.write(new_content)

        except Exception as e:
            print(f"[ERROR] Error procesando {view_file}: {e}")
            # Restaurar backup en caso de error
            shutil.copy2(backup_path, view_file)

        return correcciones

    def aplicar_mejoras_consistencia(self, view_file: Path, modulo: str) -> int:
        """Aplica mejoras automáticas de consistencia visual"""
        correcciones = 0

        try:
            with open(view_file, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # 1. Estandarizar colores
            for color_viejo, color_nuevo in self.design_standards[
                "colores_primarios"
            ].items():
                if color_viejo in content:
                    content = content.replace(color_viejo, color_nuevo)
                    correcciones += 1
                    self.corrections_applied.append(
                        f"{modulo}: Color {color_viejo} cambiado a {color_nuevo}"
                    )

            # 2. Estandarizar fuentes
            font_pattern = r'QFont\(["\']([^"\']*)["\']'
            fuentes_encontradas = re.findall(font_pattern, content)

            for fuente in fuentes_encontradas:
                if fuente not in [
                    self.design_standards["fuente_estandar"],
                    "Courier New",
                ]:
                    content = content.replace(
                        f'QFont("{fuente}"',
                        f'QFont("{self.design_standards["fuente_estandar"]}"',
                    )
                    content = content.replace(
                        f"QFont('{fuente}'",
                        f"QFont('{self.design_standards['fuente_estandar']}'",
                    )
                    correcciones += 1
                    self.corrections_applied.append(
                        f"{modulo}: Fuente {fuente} cambiada a {self.design_standards['fuente_estandar']}"
                    )

            # 3. Estandarizar espaciado
            spacing_pattern = r"setSpacing\((\d+)\)"
            espaciados = re.findall(spacing_pattern, content)

            for espaciado in espaciados:
                espaciado_int = int(espaciado)
                if espaciado_int not in self.design_standards["espaciado_estandar"]:
                    # Encontrar el valor estándar más cercano
                    espaciado_nuevo = min(
                        self.design_standards["espaciado_estandar"],
                        key=lambda x: abs(x - espaciado_int),
                    )
                    content = content.replace(
                        f"setSpacing({espaciado})", f"setSpacing({espaciado_nuevo})"
                    )
                    correcciones += 1
                    self.corrections_applied.append(
                        f"{modulo}: Espaciado {espaciado} ajustado a {espaciado_nuevo}"
                    )

            # Guardar cambios si hubo modificaciones
            if content != original_content:
                with open(view_file, "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception as e:
            print(f"[ERROR] Error procesando consistencia en {view_file}: {e}")

        return correcciones

    def _generar_nombre_accesible(self, variable_name: str) -> str:
        """Genera un nombre accesible basado en el nombre de la variable"""
        # Convertir camelCase/snake_case a texto legible
        name = re.sub(r"([A-Z])", r" \1", variable_name)
        name = name.replace("_", " ")
        name = name.strip().title()

        # Mejoras específicas
        name = name.replace("Btn", "Botón")
        name = name.replace("Edit", "Campo de")
        name = name.replace("Label", "Etiqueta")
        name = name.replace("Combo", "Lista desplegable")

        return name

    def _generar_tooltip(self, variable_name: str) -> str:
        """Genera un tooltip descriptivo basado en el nombre de la variable"""
        base_name = self._generar_nombre_accesible(variable_name)

        # Tooltips específicos por tipo
        if "guardar" in variable_name.lower():
            return f"Guardar cambios - {base_name}"
        elif "eliminar" in variable_name.lower() or "delete" in variable_name.lower():
            return f"Eliminar elemento - {base_name}"
        elif "editar" in variable_name.lower() or "edit" in variable_name.lower():
            return f"Editar información - {base_name}"
        elif "buscar" in variable_name.lower() or "search" in variable_name.lower():
            return f"Buscar elementos - {base_name}"
        elif "nuevo" in variable_name.lower() or "add" in variable_name.lower():
            return f"Agregar nuevo elemento - {base_name}"
        else:
            return f"Acción: {base_name}"

    def crear_archivo_estilos_centralizados(self):
        """Crea un archivo de estilos centralizados"""
        styles_content = '''"""
Estilos UI/UX Centralizados para Rexus.app
Archivo generado automáticamente
"""

from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

class RexusStyles:
    """Estilos estandarizados para toda la aplicación"""
    
    # Colores del sistema
    COLOR_PRIMARIO = "#2E7D32"      # Verde oscuro
    COLOR_SECUNDARIO = "#388E3C"    # Verde medio  
    COLOR_ACENTO = "#4CAF50"        # Verde claro
    COLOR_INFO = "#1976D2"          # Azul
    COLOR_ADVERTENCIA = "#FF9800"   # Naranja
    COLOR_ERROR = "#F44336"         # Rojo
    COLOR_EXITO = "#4CAF50"         # Verde
    
    # Fuentes estandarizadas
    FUENTE_PRINCIPAL = "Arial"
    FUENTE_MONOSPACE = "Courier New"
    
    # Tamaños de fuente
    TAMAÑO_TITULO = 16
    TAMAÑO_SUBTITULO = 14
    TAMAÑO_NORMAL = 11
    TAMAÑO_PEQUEÑO = 9
    
    # Espaciado estándar
    ESPACIADO_PEQUENO = 5
    ESPACIADO_NORMAL = 10
    ESPACIADO_GRANDE = 15
    ESPACIADO_EXTRA = 20
    
    # Márgenes estándar
    MARGEN_PEQUENO = 5
    MARGEN_NORMAL = 10
    MARGEN_GRANDE = 15
    MARGEN_EXTRA = 20
    
    @staticmethod
    def fuente_titulo():
        """Retorna fuente para títulos"""
        font = QFont(RexusStyles.FUENTE_PRINCIPAL, RexusStyles.TAMAÑO_TITULO)
        font.setBold(True)
        return font
        
    @staticmethod
    def fuente_subtitulo():
        """Retorna fuente para subtítulos"""
        font = QFont(RexusStyles.FUENTE_PRINCIPAL, RexusStyles.TAMAÑO_SUBTITULO)
        font.setBold(True)
        return font
        
    @staticmethod
    def fuente_normal():
        """Retorna fuente normal"""
        return QFont(RexusStyles.FUENTE_PRINCIPAL, RexusStyles.TAMAÑO_NORMAL)
        
    @staticmethod
    def fuente_monospace():
        """Retorna fuente monospace"""
        return QFont(RexusStyles.FUENTE_MONOSPACE, RexusStyles.TAMAÑO_NORMAL)
        
    @staticmethod
    def color_primario():
        """Retorna color primario como QColor"""
        return QColor(RexusStyles.COLOR_PRIMARIO)
        
    @staticmethod
    def estilo_boton_primario():
        """Retorna stylesheet para botón primario"""
        return f"""
        QPushButton {{
            background-color: {RexusStyles.COLOR_PRIMARIO};
            color: white;
            border: 2px solid {RexusStyles.COLOR_PRIMARIO};
            border-radius: 5px;
            padding: 8px 16px;
            font-family: {RexusStyles.FUENTE_PRINCIPAL};
            font-size: {RexusStyles.TAMAÑO_NORMAL}px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {RexusStyles.COLOR_SECUNDARIO};
            border-color: {RexusStyles.COLOR_SECUNDARIO};
        }}
        QPushButton:pressed {{
            background-color: {RexusStyles.COLOR_ACENTO};
        }}
        QPushButton:disabled {{
            background-color: #CCCCCC;
            color: #666666;
            border-color: #CCCCCC;
        }}
        """
        
    @staticmethod
    def estilo_input():
        """Retorna stylesheet para campos de entrada"""
        return f"""
        QLineEdit, QTextEdit {{
            border: 2px solid #DDDDDD;
            border-radius: 4px;
            padding: 5px;
            font-family: {RexusStyles.FUENTE_PRINCIPAL};
            font-size: {RexusStyles.TAMAÑO_NORMAL}px;
            background-color: white;
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border-color: {RexusStyles.COLOR_PRIMARIO};
        }}
        QLineEdit:disabled, QTextEdit:disabled {{
            background-color: #F5F5F5;
            color: #666666;
        }}
        """
        
    @staticmethod
    def estilo_tabla():
        """Retorna stylesheet para tablas"""
        return f"""
        QTableWidget {{
            gridline-color: #DDDDDD;
            background-color: white;
            alternate-background-color: #F9F9F9;
            selection-background-color: {RexusStyles.COLOR_ACENTO};
            font-family: {RexusStyles.FUENTE_PRINCIPAL};
            font-size: {RexusStyles.TAMAÑO_NORMAL}px;
        }}
        QTableWidget::item {{
            padding: 5px;
            border: none;
        }}
        QHeaderView::section {{
            background-color: {RexusStyles.COLOR_PRIMARIO};
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }}
        """
'''

        styles_path = self.root_path / "utils" / "rexus_styles.py"
        styles_path.parent.mkdir(exist_ok=True)

        with open(styles_path, "w", encoding="utf-8") as f:
            f.write(styles_content)

        self.corrections_applied.append(
            "GLOBAL: Creado archivo de estilos centralizados"
        )
        return styles_path

    def procesar_todos_los_modulos(self):
        """Procesa todos los módulos aplicando mejoras UI/UX"""
        print("=" * 60)
        print("APLICADOR DE MEJORAS UI/UX - REXUS APP")
        print("=" * 60)

        if not self.modules_path.exists():
            print(f"[ERROR] No se encuentra el directorio: {self.modules_path}")
            return

        # Crear archivo de estilos centralizados
        print("[INFO] Creando sistema de estilos centralizados...")
        styles_path = self.crear_archivo_estilos_centralizados()
        print(f"[SUCCESS] Estilos creados en: {styles_path}")

        # Procesar módulos
        modulos = [
            d
            for d in self.modules_path.iterdir()
            if d.is_dir() and not d.name.startswith("__")
        ]
        total_correcciones = 0

        for modulo in modulos:
            print(f"\n[MODULO] Procesando: {modulo.name}")

            view_files = list(modulo.glob("**/view.py"))

            for view_file in view_files:
                print(f"  [FILE] Procesando: {view_file.name}")

                # Aplicar mejoras de accesibilidad
                acc_fixes = self.aplicar_mejoras_accesibilidad(view_file, modulo.name)

                # Aplicar mejoras de consistencia
                cons_fixes = self.aplicar_mejoras_consistencia(view_file, modulo.name)

                fixes_total = acc_fixes + cons_fixes
                total_correcciones += fixes_total

                if fixes_total > 0:
                    print(f"    [SUCCESS] {fixes_total} correcciones aplicadas")
                else:
                    print(f"    [INFO] Sin correcciones necesarias")

        # Generar reporte de correcciones
        self.generar_reporte_correcciones(total_correcciones)

        return total_correcciones

    def generar_reporte_correcciones(self, total_correcciones: int):
        """Genera reporte de las correcciones aplicadas"""
        print("\n" + "=" * 60)
        print("REPORTE DE CORRECCIONES APLICADAS")
        print("=" * 60)
        print(f"Total de correcciones: {total_correcciones}")
        print(f"Backups creados en: {self.backups_path}")

        # Guardar reporte detallado
        try:
            logs_path = self.root_path / "logs"
            logs_path.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            reporte_path = logs_path / f"ui_ux_fixes_report_{timestamp}.json"

            import json

            reporte = {
                "timestamp": timestamp,
                "total_correcciones": total_correcciones,
                "correcciones_detalle": self.corrections_applied,
                "backups_path": str(self.backups_path),
            }

            with open(reporte_path, "w", encoding="utf-8") as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)

            print(f"[SUCCESS] Reporte guardado en: {reporte_path}")

        except Exception as e:
            print(f"[ERROR] No se pudo guardar el reporte: {e}")

        # Mostrar resumen de correcciones por tipo
        tipos_correcciones = {}
        for correccion in self.corrections_applied:
            if "nombre accesible" in correccion:
                tipos_correcciones["Accesibilidad - Nombres"] = (
                    tipos_correcciones.get("Accesibilidad - Nombres", 0) + 1
                )
            elif "tooltip" in correccion:
                tipos_correcciones["Accesibilidad - Tooltips"] = (
                    tipos_correcciones.get("Accesibilidad - Tooltips", 0) + 1
                )
            elif "Color" in correccion:
                tipos_correcciones["Consistencia - Colores"] = (
                    tipos_correcciones.get("Consistencia - Colores", 0) + 1
                )
            elif "Fuente" in correccion:
                tipos_correcciones["Consistencia - Fuentes"] = (
                    tipos_correcciones.get("Consistencia - Fuentes", 0) + 1
                )
            elif "Espaciado" in correccion:
                tipos_correcciones["Consistencia - Espaciado"] = (
                    tipos_correcciones.get("Consistencia - Espaciado", 0) + 1
                )

        print("\nCORRECCIONES POR TIPO:")
        for tipo, cantidad in tipos_correcciones.items():
            print(f"  {tipo}: {cantidad}")

        print(f"\n[SUCCESS] Mejoras UI/UX aplicadas exitosamente!")
        print(f"[INFO] Se recomienda probar la aplicación para verificar los cambios")


def main():
    """Función principal"""
    fixer = UIUXFixer()
    total_fixes = fixer.procesar_todos_los_modulos()

    if total_fixes and total_fixes > 0:
        print(f"\n[COMPLETE] Proceso finalizado con {total_fixes} mejoras aplicadas")
    else:
        print("\n[INFO] No se encontraron elementos que requieran corrección")


if __name__ == "__main__":
    main()
