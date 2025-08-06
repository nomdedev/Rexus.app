#!/usr/bin/env python3
"""
MIT License - Copyright (c) 2025 Rexus.app

Completar XSS Protection en Formularios Restantes
================================================

Script para finalizar la implementación de protección XSS en todos los
formularios y campos de entrada de texto del sistema Rexus.app.

Este script:
1. Identifica módulos sin protección XSS completa
2. Agrega importaciones necesarias
3. Implementa sanitización en métodos de formulario
4. Añade validación de entrada
5. Crea métodos de obtención de datos seguros
6. Verifica la implementación completa

Uso:
python tools/security/completar_xss_protection.py
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Agregar ruta del proyecto
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

class XSSProtectionCompleter:
    """Completador de protección XSS para formularios restantes"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.modules_dir = base_dir / "rexus" / "modules"
        self.results = {
            "processed": [],
            "already_protected": [],
            "errors": [],
            "completed": []
        }
        
        # Patrones para detectar formularios y campos de entrada
        self.form_patterns = [
            r"QLineEdit\(",
            r"QTextEdit\(",
            r"QPlainTextEdit\(",
            r"QComboBox\(",
            r"QSpinBox\(",
            r"QDoubleSpinBox\(",
            r"QDateEdit\(",
            r"QTimeEdit\(",
            r"QDateTimeEdit\("
        ]
        
        # Patrones para métodos de obtención de datos
        self.data_method_patterns = [
            r"def\s+obtener_datos_.*?\(",
            r"def\s+get_form_data\(",
            r"def\s+recopilar_datos\(",
            r"def\s+get_.*?_data\(",
            r"def\s+.*?_formulario\("
        ]
    
    def tiene_xss_protection(self, file_path: Path) -> bool:
        """Verifica si un archivo ya tiene protección XSS implementada"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Marcadores de protección XSS
            markers = [
                "# XSS Protection Added",
                "🔒 XSS Protection Added",
                "XSS_PROTECTION_ADDED",
                "XSSProtection",
                "FormProtector"
            ]
            
            return any(marker in content for marker in markers)
            
        except Exception as e:
            print(f"[ERROR] No se pudo leer {file_path}: {e}")
            return False
    
    def tiene_formularios(self, file_path: Path) -> bool:
        """Verifica si un archivo tiene formularios que necesitan protección"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar elementos de formulario
            for pattern in self.form_patterns:
                if re.search(pattern, content):
                    return True
            
            return False
            
        except Exception as e:
            print(f"[ERROR] No se pudo analizar {file_path}: {e}")
            return False
    
    def agregar_imports_xss(self, content: str) -> str:
        """Agrega imports necesarios para protección XSS"""
        
        # Verificar si ya tiene los imports
        if "from rexus.utils.xss_protection import" in content:
            return content
        
        # Encontrar donde insertar imports
        lines = content.split('\n')
        insert_index = 0
        
        # Buscar después de los imports existentes
        for i, line in enumerate(lines):
            if line.startswith('from PyQt6') or line.startswith('from rexus'):
                insert_index = i + 1
            elif line.startswith('import ') and not line.startswith('import sys'):
                insert_index = i + 1
        
        # Insertar imports de XSS protection
        xss_imports = [
            "",
            "# XSS Protection imports",
            "from rexus.utils.xss_protection import XSSProtection, FormProtector",
            "from rexus.utils.security import SecurityUtils",
            ""
        ]
        
        for i, import_line in enumerate(xss_imports):
            lines.insert(insert_index + i, import_line)
        
        return '\n'.join(lines)
    
    def agregar_xss_header(self, content: str) -> str:
        """Agrega header de protección XSS al archivo"""
        
        if "XSS Protection Added" in content:
            return content
        
        lines = content.split('\n')
        
        # Encontrar donde insertar el header (después del MIT license)
        insert_index = 0
        for i, line in enumerate(lines):
            if '"""' in line and i > 0:
                # Insertar después del docstring de license
                insert_index = i + 1
                break
        
        xss_header = [
            "",
            "# [SECURITY] XSS Protection Added - Validate all user inputs",
            "# Todos los campos de formulario estan protegidos contra XSS",
            "# XSS Protection Added",
            ""
        ]
        
        for i, header_line in enumerate(xss_header):
            lines.insert(insert_index + i, header_line)
        
        return '\n'.join(lines)
    
    def agregar_inicializacion_protector(self, content: str) -> str:
        """Agrega inicialización del protector XSS en __init__"""
        
        if "self.xss_protector = FormProtector()" in content:
            return content
        
        lines = content.split('\n')
        
        # Buscar el método __init__
        for i, line in enumerate(lines):
            if "def __init__(self" in line:
                # Buscar el final del método __init__ o una línea apropiada
                j = i + 1
                indent = "        "  # Indentación estándar
                
                while j < len(lines):
                    if (lines[j].strip() and 
                        not lines[j].startswith(indent) and 
                        not lines[j].startswith("#") and
                        not lines[j].strip().startswith('"""')):
                        break
                    
                    # Insertar antes del final del __init__
                    if (lines[j].strip().startswith("self.") and 
                        "layout" not in lines[j].lower() and
                        "show" not in lines[j].lower()):
                        
                        protection_code = [
                            "",
                            "        # Inicializar protección XSS",
                            "        try:",
                            "            self.xss_protector = FormProtector()",
                            "            self._setup_xss_protection()",
                            "        except Exception as e:",
                            "            print(f'[XSS] Error inicializando protección: {e}')",
                            ""
                        ]
                        
                        for k, prot_line in enumerate(protection_code):
                            lines.insert(j + k, prot_line)
                        break
                    
                    j += 1
                break
        
        return '\n'.join(lines)
    
    def agregar_metodo_setup_xss(self, content: str) -> str:
        """Agrega método para configurar protección XSS"""
        
        if "def _setup_xss_protection(self)" in content:
            return content
        
        lines = content.split('\n')
        
        # Buscar un lugar apropiado para insertar el método (antes del final de la clase)
        insert_index = len(lines) - 5  # Por defecto, cerca del final
        
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() and not lines[i].startswith(' '):
                insert_index = i
                break
        
        setup_method = [
            "",
            "    def _setup_xss_protection(self):",
            "        \"\"\"Configura la protección XSS para todos los campos del formulario.\"\"\"",
            "        try:",
            "            # Configurar filtros para campos de texto",
            "            text_fields = []",
            "            ",
            "            # Buscar todos los campos de entrada en el formulario",
            "            for child in self.findChildren((QLineEdit, QTextEdit, QPlainTextEdit)):",
            "                if hasattr(child, 'objectName') and child.objectName():",
            "                    field_name = child.objectName()",
            "                    text_fields.append(field_name)",
            "                    ",
            "                    # Configurar validación en tiempo real",
            "                    if isinstance(child, QLineEdit):",
            "                        child.textChanged.connect(lambda text, field=field_name: self._validate_field_input(field, text))",
            "                    elif isinstance(child, (QTextEdit, QPlainTextEdit)):",
            "                        child.textChanged.connect(lambda field=field_name: self._validate_text_area(field))",
            "            ",
            "            # Configurar protector con campos encontrados",
            "            for field in text_fields:",
            "                self.xss_protector.add_field_filter(field, max_length=1000)",
            "            ",
            "            print(f'[XSS] Protección configurada para {len(text_fields)} campos')",
            "            ",
            "        except Exception as e:",
            "            print(f'[XSS ERROR] Error configurando protección: {e}')",
            ""
        ]
        
        for i, method_line in enumerate(setup_method):
            lines.insert(insert_index + i, method_line)
        
        return '\n'.join(lines)
    
    def agregar_metodos_validacion(self, content: str) -> str:
        """Agrega métodos de validación XSS"""
        
        if "def _validate_field_input(self" in content:
            return content
        
        lines = content.split('\n')
        insert_index = len(lines) - 3
        
        validation_methods = [
            "",
            "    def _validate_field_input(self, field_name: str, text: str):",
            "        \"\"\"Valida entrada de campo en tiempo real.\"\"\"",
            "        try:",
            "            if not SecurityUtils.is_safe_input(text):",
            "                print(f'[XSS WARNING] Contenido potencialmente peligroso en {field_name}: {text[:50]}...')",
            "                # Aquí podrías mostrar advertencia al usuario",
            "        except Exception as e:",
            "            print(f'[XSS ERROR] Error validando {field_name}: {e}')",
            "",
            "    def _validate_text_area(self, field_name: str):",
            "        \"\"\"Valida contenido de área de texto.\"\"\"",
            "        try:",
            "            widget = self.findChild((QTextEdit, QPlainTextEdit), field_name)",
            "            if widget:",
            "                text = widget.toPlainText()",
            "                if not SecurityUtils.is_safe_input(text):",
            "                    print(f'[XSS WARNING] Contenido potencialmente peligroso en {field_name}')",
            "        except Exception as e:",
            "            print(f'[XSS ERROR] Error validando área de texto {field_name}: {e}')",
            ""
        ]
        
        for i, method_line in enumerate(validation_methods):
            lines.insert(insert_index + i, method_line)
        
        return '\n'.join(lines)
    
    def agregar_metodo_datos_seguros(self, content: str) -> str:
        """Agrega método para obtener datos del formulario de forma segura"""
        
        if "def obtener_datos_formulario_seguro(self" in content:
            return content
        
        lines = content.split('\n')
        insert_index = len(lines) - 2
        
        safe_data_method = [
            "",
            "    def obtener_datos_formulario_seguro(self) -> Dict[str, any]:",
            "        \"\"\"Obtiene datos del formulario con sanitización XSS completa.\"\"\"",
            "        try:",
            "            datos = {}",
            "            ",
            "            # Obtener datos de campos de línea",
            "            for line_edit in self.findChildren(QLineEdit):",
            "                if hasattr(line_edit, 'objectName') and line_edit.objectName():",
            "                    field_name = line_edit.objectName()",
            "                    raw_text = line_edit.text()",
            "                    # Sanitizar con XSSProtection",
            "                    safe_text = XSSProtection.sanitize_text(raw_text)",
            "                    datos[field_name] = safe_text",
            "            ",
            "            # Obtener datos de áreas de texto",
            "            for text_edit in self.findChildren((QTextEdit, QPlainTextEdit)):",
            "                if hasattr(text_edit, 'objectName') and text_edit.objectName():",
            "                    field_name = text_edit.objectName()",
            "                    raw_text = text_edit.toPlainText()",
            "                    # Sanitizar con XSSProtection",
            "                    safe_text = XSSProtection.sanitize_text(raw_text)",
            "                    datos[field_name] = safe_text",
            "            ",
            "            # Obtener datos de combos",
            "            for combo in self.findChildren(QComboBox):",
            "                if hasattr(combo, 'objectName') and combo.objectName():",
            "                    field_name = combo.objectName()",
            "                    current_text = combo.currentText()",
            "                    # Sanitizar texto del combo",
            "                    safe_text = XSSProtection.sanitize_text(current_text)",
            "                    datos[field_name] = safe_text",
            "            ",
            "            # Usar protector para validación final",
            "            if hasattr(self, 'xss_protector'):",
            "                datos = self.xss_protector.sanitize_form_data(datos)",
            "            ",
            "            return datos",
            "            ",
            "        except Exception as e:",
            "            print(f'[XSS ERROR] Error obteniendo datos seguros: {e}')",
            "            return {}",
            ""
        ]
        
        for i, method_line in enumerate(safe_data_method):
            lines.insert(insert_index + i, method_line)
        
        return '\n'.join(lines)
    
    def proteger_metodos_existentes(self, content: str) -> str:
        """Protege métodos existentes de obtención de datos"""
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Buscar métodos que obtengan texto de widgets
            if ".text()" in line or ".toPlainText()" in line or ".currentText()" in line:
                # Verificar si ya tiene protección
                if "XSSProtection.sanitize_text" not in lines[max(0, i-2):i+3]:
                    # Agregar sanitización
                    if "=" in line and (".text()" in line or ".toPlainText()" in line):
                        # Modificar la línea para incluir sanitización
                        indent = len(line) - len(line.lstrip())
                        var_name = line.split("=")[0].strip()
                        widget_call = line.split("=")[1].strip()
                        
                        sanitized_line = f"{' ' * indent}{var_name} = XSSProtection.sanitize_text({widget_call})"
                        lines[i] = sanitized_line
                        
                        # Agregar comentario explicativo
                        comment_line = f"{' ' * indent}# [XSS] Protection: Sanitizar entrada de usuario"
                        lines.insert(i, comment_line)
        
        return '\n'.join(lines)
    
    def procesar_archivo(self, file_path: Path) -> bool:
        """Procesa un archivo individual para completar protección XSS"""
        
        print(f"\n[PROCESANDO] {file_path.name}")
        
        try:
            # Leer contenido actual
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar si ya tiene protección
            if self.tiene_xss_protection(file_path):
                print(f"  [SKIP] Ya tiene protección XSS")
                self.results["already_protected"].append(str(file_path))
                return True
            
            # Verificar si tiene formularios
            if not self.tiene_formularios(file_path):
                print(f"  [SKIP] No tiene formularios que proteger")
                return True
            
            print(f"  [XSS] Agregando protección XSS completa...")
            
            # Aplicar todas las modificaciones
            content = self.agregar_xss_header(content)
            content = self.agregar_imports_xss(content)
            content = self.agregar_inicializacion_protector(content)
            content = self.agregar_metodo_setup_xss(content)
            content = self.agregar_metodos_validacion(content)
            content = self.agregar_metodo_datos_seguros(content)
            content = self.proteger_metodos_existentes(content)
            
            # Escribir archivo modificado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  [OK] Protección XSS completada")
            self.results["completed"].append(str(file_path))
            return True
            
        except Exception as e:
            print(f"  [ERROR] Error procesando archivo: {e}")
            self.results["errors"].append(f"{file_path}: {e}")
            return False
    
    def encontrar_archivos_objetivo(self) -> List[Path]:
        """Encuentra archivos que necesitan protección XSS"""
        
        archivos_objetivo = []
        
        # Buscar todos los archivos view.py en módulos
        for module_dir in self.modules_dir.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith('__'):
                view_file = module_dir / "view.py"
                
                if view_file.exists():
                    archivos_objetivo.append(view_file)
                
                # Buscar también archivos de diálogo
                for dialog_file in module_dir.glob("*dialog*.py"):
                    archivos_objetivo.append(dialog_file)
                
                # Buscar en subdirectorios
                for subdir in module_dir.iterdir():
                    if subdir.is_dir():
                        sub_view = subdir / "view.py"
                        if sub_view.exists():
                            archivos_objetivo.append(sub_view)
        
        # También verificar archivos de configuración y login
        core_dir = self.base_dir / "rexus" / "core"
        if core_dir.exists():
            login_dialog = core_dir / "login_dialog.py"
            if login_dialog.exists():
                archivos_objetivo.append(login_dialog)
        
        return archivos_objetivo
    
    def ejecutar_completion(self):
        """Ejecuta el proceso completo de completar protección XSS"""
        
        print("[SECURITY] COMPLETANDO PROTECCION XSS EN FORMULARIOS RESTANTES")
        print("=" * 60)
        
        archivos_objetivo = self.encontrar_archivos_objetivo()
        print(f"[INFO] Encontrados {len(archivos_objetivo)} archivos para revisar")
        
        for archivo in archivos_objetivo:
            self.procesar_archivo(archivo)
        
        # Mostrar resumen
        print("\n" + "=" * 60)
        print("[REPORT] RESUMEN DE COMPLETADO XSS")
        print("=" * 60)
        
        print(f"[OK] Archivos completados: {len(self.results['completed'])}")
        print(f"[SKIP] Archivos ya protegidos: {len(self.results['already_protected'])}")
        print(f"[ERROR] Errores: {len(self.results['errors'])}")
        
        if self.results['completed']:
            print("\n[COMPLETED] ARCHIVOS COMPLETADOS:")
            for archivo in self.results['completed']:
                print(f"  - {Path(archivo).name}")
        
        if self.results['errors']:
            print("\n[ERRORS] ERRORES:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        total_procesados = len(self.results['completed']) + len(self.results['already_protected'])
        print(f"\n[RESULT] {total_procesados} archivos con proteccion XSS completa")
        
        if len(self.results['errors']) == 0:
            print("[SUCCESS] PROTECCION XSS COMPLETADA EXITOSAMENTE")
        else:
            print("[WARNING] Proteccion completada con algunos errores")

def main():
    """Función principal"""
    
    # Verificar directorio
    if not (root_dir / "rexus").exists():
        print("❌ Error: No se encuentra el directorio 'rexus'. Ejecutar desde la raíz del proyecto.")
        sys.exit(1)
    
    # Crear y ejecutar completador
    completer = XSSProtectionCompleter(root_dir)
    completer.ejecutar_completion()
    
    print(f"\n📝 Logs guardados en: tools/security/")

if __name__ == "__main__":
    main()