#!/usr/bin/env python3
"""
Script para implementar paginación en tablas grandes de Rexus.app
"""

import os
import re
from pathlib import Path


class PaginationImplementer:
    def __init__(self):
        self.base_path = Path.cwd()
        self.modules_path = self.base_path / "rexus" / "modules"
        self.modulos_criticos = ["inventario", "obras", "pedidos", "compras", "usuarios"]
        self.implementaciones_exitosas = []

    def implementar_paginacion_completa(self):
        """Implementa paginación en todos los módulos críticos"""
        print("[PAGINATION] IMPLEMENTANDO PAGINACION EN MODULOS CRITICOS")
        print("=" * 60)

        for modulo in self.modulos_criticos:
            print(f"\n[INFO] Procesando módulo: {modulo}")
            self.implementar_paginacion_modulo(modulo)

        self.generar_reporte_final()

    def implementar_paginacion_modulo(self, nombre_modulo):
        """Implementa paginación en un módulo específico"""
        modulo_path = self.modules_path / nombre_modulo

        if not modulo_path.exists():
            print(f"  [SKIP] Módulo {nombre_modulo} no existe")
            return

        # Verificar archivos del módulo
        view_file = modulo_path / "view.py"
        controller_file = modulo_path / "controller.py"
        model_file = modulo_path / "model.py"

        if not all([view_file.exists(), controller_file.exists(), model_file.exists()]):
            print(f"  [SKIP] Módulo {nombre_modulo} incompleto")
            return

        # Implementar en cada archivo
        view_updated = self.agregar_paginacion_view(view_file)
        controller_updated = self.agregar_paginacion_controller(controller_file)
        model_updated = self.agregar_paginacion_model(model_file)

        if any([view_updated, controller_updated, model_updated]):
            self.implementaciones_exitosas.append(nombre_modulo)
            print(f"  [OK] Paginación implementada en {nombre_modulo}")
        else:
            print(f"  [SKIP] Paginación ya existe en {nombre_modulo}")

    def agregar_paginacion_view(self, view_file):
        """Agrega componentes de paginación a la vista"""
        try:
            with open(view_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Verificar si ya tiene paginación
            if "QPushButton" in content and \
                ("página" in content.lower() or "page" in content.lower()):
                return False

            # Agregar imports necesarios si no existen
            if "from PyQt6.QtWidgets import" in content and \
                "QSpinBox" not in content:
                # Agregar QSpinBox y QLabel a los imports
                content = re.sub(
                    r'from PyQt6\.QtWidgets import \((.*?)\)',
                    lambda m: f"from PyQt6.QtWidgets import ({m.group(1)},\n    QSpinBox,\n    QLabel)",
                    content,
                    flags=re.DOTALL
                )

            # Agregar método de paginación a la clase principal
            pagination_code = '''
    def crear_controles_paginacion(self):
        """Crea los controles de paginación"""
        paginacion_layout = QHBoxLayout()

        # Etiqueta de información
        self.info_label = QLabel("Mostrando 1-50 de 0 registros")
        paginacion_layout.addWidget(self.info_label)

        paginacion_layout.addStretch()

        # Controles de navegación
        self.btn_primera = QPushButton("<<")
        self.btn_primera.setMaximumWidth(40)
        self.btn_primera.clicked.connect(lambda: self.ir_a_pagina(1))
        paginacion_layout.addWidget(self.btn_primera)

        self.btn_anterior = QPushButton("<")
        self.btn_anterior.setMaximumWidth(30)
        self.btn_anterior.clicked.connect(self.pagina_anterior)
        paginacion_layout.addWidget(self.btn_anterior)

        # Control de página actual
        self.pagina_actual_spin = QSpinBox()
        self.pagina_actual_spin.setMinimum(1)
        self.pagina_actual_spin.setMaximum(1)
        self.pagina_actual_spin.valueChanged.connect(self.cambiar_pagina)
        self.pagina_actual_spin.setMaximumWidth(60)
        paginacion_layout.addWidget(QLabel("Página:"))
        paginacion_layout.addWidget(self.pagina_actual_spin)

        self.total_paginas_label = QLabel("de 1")
        paginacion_layout.addWidget(self.total_paginas_label)

        self.btn_siguiente = QPushButton(">")
        self.btn_siguiente.setMaximumWidth(30)
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)
        paginacion_layout.addWidget(self.btn_siguiente)

        self.btn_ultima = QPushButton(">>")
        self.btn_ultima.setMaximumWidth(40)
        self.btn_ultima.clicked.connect(self.ultima_pagina)
        paginacion_layout.addWidget(self.btn_ultima)

        # Selector de registros por página
        paginacion_layout.addWidget(QLabel("Registros por página:"))
        self.registros_por_pagina_combo = QComboBox()
        self.registros_por_pagina_combo.addItems(["25", "50", "100", "200"])
        self.registros_por_pagina_combo.setCurrentText("50")
        self.registros_por_pagina_combo.currentTextChanged.connect(self.cambiar_registros_por_pagina)
        paginacion_layout.addWidget(self.registros_por_pagina_combo)

        return paginacion_layout

    def actualizar_controles_paginacion(self,
pagina_actual,
        total_paginas,
        total_registros,
        registros_mostrados):
        """Actualiza los controles de paginación"""
        if hasattr(self, 'info_label'):
            inicio = ((pagina_actual - 1) * int(self.registros_por_pagina_combo.currentText())) + 1
            fin = min(inicio + registros_mostrados - 1, total_registros)
            self.info_label.setText(f"Mostrando {inicio}-{fin} de {total_registros} registros")

        if hasattr(self, 'pagina_actual_spin'):
            self.pagina_actual_spin.blockSignals(True)
            self.pagina_actual_spin.setValue(pagina_actual)
            self.pagina_actual_spin.setMaximum(max(1, total_paginas))
            self.pagina_actual_spin.blockSignals(False)

        if hasattr(self, 'total_paginas_label'):
            self.total_paginas_label.setText(f"de {total_paginas}")

        # Habilitar/deshabilitar botones
        if hasattr(self, 'btn_primera'):
            self.btn_primera.setEnabled(pagina_actual > 1)
            self.btn_anterior.setEnabled(pagina_actual > 1)
            self.btn_siguiente.setEnabled(pagina_actual < total_paginas)
            self.btn_ultima.setEnabled(pagina_actual < total_paginas)

    def ir_a_pagina(self, pagina):
        """Va a una página específica"""
        if hasattr(self.controller, 'cargar_pagina'):
            self.controller.cargar_pagina(pagina)

    def pagina_anterior(self):
        """Va a la página anterior"""
        if hasattr(self, 'pagina_actual_spin'):
            pagina_actual = self.pagina_actual_spin.value()
            if pagina_actual > 1:
                self.ir_a_pagina(pagina_actual - 1)

    def pagina_siguiente(self):
        """Va a la página siguiente"""
        if hasattr(self, 'pagina_actual_spin'):
            pagina_actual = self.pagina_actual_spin.value()
            total_paginas = self.pagina_actual_spin.maximum()
            if pagina_actual < total_paginas:
                self.ir_a_pagina(pagina_actual + 1)

    def ultima_pagina(self):
        """Va a la última página"""
        if hasattr(self, 'pagina_actual_spin'):
            total_paginas = self.pagina_actual_spin.maximum()
            self.ir_a_pagina(total_paginas)

    def cambiar_pagina(self, pagina):
        """Cambia a la página seleccionada"""
        self.ir_a_pagina(pagina)

    def cambiar_registros_por_pagina(self, registros):
        """Cambia la cantidad de registros por página"""
        if hasattr(self.controller, 'cambiar_registros_por_pagina'):
            self.controller.cambiar_registros_por_pagina(int(registros))
'''

            # Insertar antes del último método o antes del final de la clase
            if "    def show_error" in content:
                content = content.replace("    def show_error", pagination_code + "\n    def show_error")
            elif "class " in content:
                # Buscar el final de la clase
                lines = content.split('\n')
                insert_index = -1
                for i in range(len(lines) - 1, -1, -1):
                    if lines[i].startswith('class ') or (lines[i].startswith('    def ') and not lines[i].strip().startswith('#')):
                        insert_index = i
                        break

                if insert_index > 0:
                    lines.insert(insert_index, pagination_code)
                    content = '\n'.join(lines)

            with open(view_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return True

        except Exception as e:
            print(f"  [ERROR] Error agregando paginación a vista: {e}")
            return False

    def agregar_paginacion_controller(self, controller_file):
        """Agrega lógica de paginación al controlador"""
        try:
            with open(controller_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Verificar si ya tiene paginación
            if "def cargar_pagina" in content:
                return False

            # Agregar métodos de paginación
            pagination_code = '''
    def cargar_pagina(self, pagina, registros_por_pagina=50):
        """Carga una página específica de datos"""
        try:
            if self.model:
                offset = (pagina - 1) * registros_por_pagina

                # Obtener datos paginados
                datos, total_registros = self.model.obtener_datos_paginados(
                    offset=offset,
                    limit=registros_por_pagina
                )

                if self.view:
                    # Cargar datos en la tabla
                    if hasattr(self.view, 'cargar_en_tabla'):
                        self.view.cargar_en_tabla(datos)

                    # Actualizar controles de paginación
                    total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
                    if hasattr(self.view, 'actualizar_controles_paginacion'):
                        self.view.actualizar_controles_paginacion(
                            pagina, total_paginas, total_registros, len(datos)
                        )

        except Exception as e:
            print(f"[ERROR] Error cargando página: {e}")
            if hasattr(self, 'mostrar_error'):
                self.mostrar_error("Error", f"Error cargando página: {str(e)}")

    def cambiar_registros_por_pagina(self, registros):
        """Cambia la cantidad de registros por página y recarga"""
        self.registros_por_pagina = registros
        self.cargar_pagina(1, registros)

    def obtener_total_registros(self):
        """Obtiene el total de registros disponibles"""
        try:
            if self.model:
                return self.model.obtener_total_registros()
            return 0
        except Exception as e:
            print(f"[ERROR] Error obteniendo total de registros: {e}")
            return 0
'''

            # Insertar antes de mostrar_error o al final de la clase
            if "def mostrar_error" in content:
                content = content.replace("def mostrar_error", pagination_code + "\n    def mostrar_error")
            else:
                content += pagination_code

            with open(controller_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return True

        except Exception as e:
            print(f"  [ERROR] Error agregando paginación a controlador: {e}")
            return False

    def agregar_paginacion_model(self, model_file):
        """Agrega métodos de paginación al modelo"""
        try:
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Verificar si ya tiene paginación
            if "def obtener_datos_paginados" in content:
                return False

            # Agregar métodos de paginación
            pagination_code = '''
    def obtener_datos_paginados(self, offset=0, limit=50, filtros=None):
        """
        Obtiene datos paginados de la tabla principal

        Args:
            offset: Número de registros a saltar
            limit: Número máximo de registros a devolver
            filtros: Filtros adicionales a aplicar

        Returns:
            tuple: (datos, total_registros)
        """
        try:
            if not self.db_connection:
                return [], 0

            cursor = self.db_connection.cursor()

            # Query base
            base_query = self._get_base_query()
            count_query = self._get_count_query()

            # Aplicar filtros si existen
            where_clause = ""
            params = []

            if filtros:
                where_conditions = []
                for campo, valor in filtros.items():
                    if valor:
                        where_conditions.append(f"{campo} LIKE ?")
                        params.append(f"%{valor}%")

                if where_conditions:
                    where_clause = " WHERE " + " AND ".join(where_conditions)

            # Obtener total de registros
            full_count_query = count_query + where_clause
            cursor.execute(full_count_query, params)
            total_registros = cursor.fetchone()[0]

            # Obtener datos paginados
            paginated_query = f"{base_query}{where_clause} ORDER BY id DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
            cursor.execute(paginated_query, params + [offset, limit])

            datos = []
            for row in cursor.fetchall():
                datos.append(self._row_to_dict(row, cursor.description))

            return datos, total_registros

        except Exception as e:
            print(f"[ERROR] Error obteniendo datos paginados: {e}")
            return [], 0

    def obtener_total_registros(self, filtros=None):
        """Obtiene el total de registros disponibles"""
        try:
            _,
total = self.obtener_datos_paginados(offset=0,
                limit=1,
                filtros=filtros)
            return total
        except Exception as e:
            print(f"[ERROR] Error obteniendo total de registros: {e}")
            return 0

    def _get_base_query(self):
        """Obtiene la query base para paginación (debe ser implementado por cada modelo)"""
        # Esta es una implementación genérica
        tabla_principal = getattr(self, 'tabla_principal', 'tabla_principal')
        return f"SELECT * FROM {tabla_principal}"

    def _get_count_query(self):
        """Obtiene la query de conteo (debe ser implementado por cada modelo)"""
        tabla_principal = getattr(self, 'tabla_principal', 'tabla_principal')
        return f"SELECT COUNT(*) FROM {tabla_principal}"

    def _row_to_dict(self, row, description):
        """Convierte una fila de base de datos a diccionario"""
        return {desc[0]: row[i] for i, desc in enumerate(description)}
'''

            # Insertar al final de la clase
            content += pagination_code

            with open(model_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return True

        except Exception as e:
            print(f"  [ERROR] Error agregando paginación a modelo: {e}")
            return False

    def generar_reporte_final(self):
        """Genera reporte final de implementación"""
        print("\n" + "="*60)
        print("[PAGINATION] REPORTE FINAL DE IMPLEMENTACION")
        print("="*60)

        print(f"\n[STATS] ESTADISTICAS:")
        print(f"   Módulos procesados: {len(self.modulos_criticos)}")
        print(f"   Implementaciones exitosas: {len(self.implementaciones_exitosas)}")
        print(f"   Porcentaje de éxito: {(len(self.implementaciones_exitosas)/len(self.modulos_criticos))*100:.1f}%")

        if self.implementaciones_exitosas:
            print(f"\n[SUCCESS] MODULOS CON PAGINACION IMPLEMENTADA:")
            for i, modulo in enumerate(self.implementaciones_exitosas, 1):
                print(f"   {i}. {modulo}")

        modulos_no_procesados = [m for m in self.modulos_criticos if m not in self.implementaciones_exitosas]
        if modulos_no_procesados:
            print(f"\n[INFO] MODULOS QUE YA TENIAN PAGINACION:")
            for i, modulo in enumerate(modulos_no_procesados, 1):
                print(f"   {i}. {modulo}")

        print(f"\n[NEXT] PROXIMOS PASOS:")
        print("   1. Probar la paginación en cada módulo")
        print("   2. Ajustar las queries específicas de cada modelo")
        print("   3. Implementar filtros avanzados con paginación")
        print("   4. Optimizar rendimiento con índices")

        return len(self.implementaciones_exitosas) > 0


def main():
    """Función principal"""
    print("[PAGINATION] IMPLEMENTADOR DE PAGINACION PARA TABLAS GRANDES")
    print("=" * 70)

    implementer = PaginationImplementer()

    try:
        implementer.implementar_paginacion_completa()
        print("\n[SUCCESS] Implementacion de paginacion completada")
        return True

    except Exception as e:
        print(f"\n[ERROR] Error durante implementacion: {e}")
        return False


if __name__ == "__main__":
    main()
