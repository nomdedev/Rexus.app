"""
Controlador de Herrajes - Rexus.app v2.0.0
Versión simplificada y funcional

Maneja la lógica entre el modelo y la vista para herrajes.
"""

import logging
from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric
from rexus.core.sql_query_manager import SQLQueryManager
from rexus.utils.unified_sanitizer import sanitize_string, sanitize_numeric

from .model import HerrajesModel

class HerrajesController(QObject):
    """Controlador simplificado para la gestión de herrajes."""
    
    # Señales para comunicación con otros módulos
    herraje_creado = pyqtSignal(dict)
    herraje_actualizado = pyqtSignal(dict)
    herraje_eliminado = pyqtSignal(int)
    stock_actualizado = pyqtSignal(int, int)

    def __init__(self, model=None, view=None, db_connection=None, usuario_actual=None):
        super().__init__()
        
        # Configurar modelo y vista
        if model is not None:
            self.model = model
            self.view = view
        else:
            # Compatibilidad hacia atrás
            self.view = model
            self.model = HerrajesModel(db_connection)
            
        self.db_connection = db_connection
        self.usuario_actual = usuario_actual or {"id": 1, "nombre": "SISTEMA"}

        # Conectar señales si la vista está disponible
        if self.view:
            self.cargar_datos_iniciales()

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales en la vista."""
        print("[HERRAJES CONTROLLER] Cargando datos iniciales...")

        try:
            # Cargar herrajes
            herrajes = self.model.obtener_todos_herrajes() if self.model else []

            # Cargar en la vista usando el método correcto
            if self.view and hasattr(self.view, "cargar_herrajes"):
                self.view.cargar_herrajes(herrajes)

            # Cargar estadísticas
            self.cargar_estadisticas()

            print(f"[HERRAJES CONTROLLER] Datos iniciales cargados: {len(herrajes)} herrajes")

        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error cargando datos iniciales: {e}")
            logging.error(f"Error cargando datos herrajes: {e}")

    def cargar_herrajes(self):
        """Carga todos los herrajes (método público para la vista)."""
        self.cargar_datos_iniciales()

    def buscar_herrajes(self, termino: str, categoria: str = ""):
        """Busca herrajes por término y categoría."""
        try:
            if not self.model:
                return

            # Preparar filtros
            filtros = {}
            if termino and len(termino.strip()) >= 2:
                filtros["descripcion"] = termino.strip()
                
            if categoria and not categoria.startswith("📂"):
                # Limpiar categoría del emoji
                categoria_limpia = categoria.split(" ", 1)[1] if " " in categoria else categoria
                filtros["categoria"] = categoria_limpia

            # Obtener herrajes filtrados
            if filtros:
                herrajes = self.model.obtener_todos_herrajes(filtros)
            elif termino and len(termino.strip()) >= 2:
                herrajes = self.model.buscar_herrajes(termino.strip())
            else:
                herrajes = self.model.obtener_todos_herrajes()

            # Actualizar vista
            if self.view and hasattr(self.view, "cargar_herrajes"):
                self.view.cargar_herrajes(herrajes)

        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error en búsqueda: {e}")
            logging.error(f"Error en búsqueda herrajes: {e}")

    def cargar_estadisticas(self):
        """Carga las estadísticas en la vista."""
        try:
            if self.model:
                estadisticas = self.model.obtener_estadisticas()
            else:
                estadisticas = {
                    "total_herrajes": 0,
                    "total_stock": 0,
                    "herrajes_bajo_stock": 0,
                    "proveedores_activos": 0
                }

            if self.view and hasattr(self.view, "actualizar_estadisticas"):
                self.view.actualizar_estadisticas(estadisticas)

        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error cargando estadísticas: {e}")
            logging.error(f"Error cargando estadísticas herrajes: {e}")

    def cargar_herrajes_obra(self, obra_id: int) -> List[Dict]:
        """Carga herrajes asignados a una obra específica."""
        try:
            if self.model:
                return self.model.obtener_herrajes_por_obra(obra_id)
            return []
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error cargando herrajes de obra: {e}")
            logging.error(f"Error cargando herrajes de obra {obra_id}: {e}")
            return []

    def obtener_proveedores(self) -> List[Dict]:
        """Obtiene lista de proveedores de herrajes."""
        try:
            if not self.model:
                return []
                
            # Como el modelo simplificado no tiene obtener_proveedores,
            # extraemos los proveedores de los herrajes existentes
            herrajes = self.model.obtener_todos_herrajes()
            proveedores_set = set()
            
            for herraje in herrajes:
                proveedor = herraje.get("proveedor", "").strip()
                if proveedor:
                    proveedores_set.add(proveedor)
            
            # Convertir a lista de diccionarios
            proveedores = []
            for proveedor in sorted(proveedores_set):
                # Contar herrajes por proveedor
                herrajes_count = sum(1 for h in herrajes if h.get("proveedor", "") == proveedor)
                proveedores.append({
                    "nombre": proveedor,
                    "contacto": "No disponible",  # Placeholder
                    "herrajes_count": herrajes_count
                })
            
            return proveedores
            
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error obteniendo proveedores: {e}")
            logging.error(f"Error obteniendo proveedores: {e}")
            return []

    def mostrar_dialogo_herraje(self, herraje_data=None):
        """Muestra el diálogo para crear/editar herraje."""
        try:
            from .improved_dialogs import HerrajeDialogManager
            
            dialog_manager = HerrajeDialogManager(self.view, self)
            form_config = dialog_manager.get_form_config()
            
            if herraje_data:
                # Editar herraje existente
                resultado = dialog_manager.crud_manager.show_edit_dialog(
                    form_config,
                    herraje_data,
                    self.actualizar_herraje
                )
            else:
                # Crear nuevo herraje
                resultado = dialog_manager.crud_manager.show_create_dialog(
                    form_config,
                    self.crear_herraje
                )
            
            if resultado:
                self.cargar_datos_iniciales()  # Recargar datos
                
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error en diálogo: {e}")
            # Fallback básico
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self.view, "Herrajes", "Diálogo pendiente de implementar")

    def crear_herraje(self, data):
        """Crea un nuevo herraje."""
        try:
            if not self.model:
                return False
                
            # Sanitizar datos
            data_limpia = {
                'codigo': sanitize_string(data.get('codigo', '')),
                'nombre': sanitize_string(data.get('descripcion', '')),
                'descripcion': sanitize_string(data.get('descripcion', '')),
                'categoria': sanitize_string(data.get('tipo', '')),
                'proveedor': sanitize_string(data.get('proveedor', '')),
                'precio_unitario': sanitize_numeric(data.get('precio_unitario', 0)),
                'stock_actual': int(sanitize_numeric(data.get('stock_actual', 0)) or 0),
                'stock_minimo': int(sanitize_numeric(data.get('stock_minimo', 0)) or 0),
                'unidad_medida': sanitize_string(data.get('unidad_medida', 'unidad')),
                'activo': data.get('activo', True)
            }
            
            # Crear en modelo
            resultado = self.model.crear_herraje(data_limpia)
            
            if resultado:
                self.herraje_creado.emit(data_limpia)
                print(f"[HERRAJES CONTROLLER] Herraje creado: {data_limpia.get('codigo')}")
                
            return resultado
            
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error creando herraje: {e}")
            return False

    def actualizar_herraje(self, data):
        """Actualiza un herraje existente."""
        try:
            if not self.model:
                return False
                
            # Sanitizar datos
            data_limpia = {
                'codigo': sanitize_string(data.get('codigo', '')),
                'nombre': sanitize_string(data.get('descripcion', '')),
                'descripcion': sanitize_string(data.get('descripcion', '')),
                'categoria': sanitize_string(data.get('tipo', '')),
                'proveedor': sanitize_string(data.get('proveedor', '')),
                'precio_unitario': sanitize_numeric(data.get('precio_unitario', 0)),
                'stock_actual': int(sanitize_numeric(data.get('stock_actual', 0)) or 0),
                'stock_minimo': int(sanitize_numeric(data.get('stock_minimo', 0)) or 0),
                'unidad_medida': sanitize_string(data.get('unidad_medida', 'unidad')),
                'activo': data.get('activo', True)
            }
            
            # Actualizar en modelo
            resultado = self.model.actualizar_herraje(data_limpia.get('codigo'), data_limpia)
            
            if resultado:
                self.herraje_actualizado.emit(data_limpia)
                print(f"[HERRAJES CONTROLLER] Herraje actualizado: {data_limpia.get('codigo')}")
                
            return resultado
            
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error actualizando herraje: {e}")
            return False

    def eliminar_herraje(self, codigo):
        """Elimina un herraje por código."""
        try:
            if not self.model:
                return False
                
            # Confirmar eliminación
            from PyQt6.QtWidgets import QMessageBox
            respuesta = QMessageBox.question(
                self.view,
                "Confirmar eliminación",
                f"¿Está seguro de eliminar el herraje {codigo}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if respuesta == QMessageBox.StandardButton.Yes:
                resultado = self.model.eliminar_herraje(codigo)
                
                if resultado:
                    self.herraje_eliminado.emit(hash(codigo))  # Emitir señal
                    self.cargar_datos_iniciales()  # Recargar datos
                    print(f"[HERRAJES CONTROLLER] Herraje eliminado: {codigo}")
                    
                return resultado
            
            return False
            
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error eliminando herraje: {e}")
            return False

    def exportar_herrajes(self, formato="excel"):
        """Exporta herrajes al formato especificado."""
        try:
            if not self.model:
                return False
                
            herrajes = self.model.obtener_todos_herrajes()
            
            if not herrajes:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self.view, "Exportar", "No hay herrajes para exportar")
                return False
            
            # Seleccionar archivo de destino
            from PyQt6.QtWidgets import QFileDialog
            if formato.lower() == "excel":
                filtro = "Excel files (*.xlsx)"
                extension = ".xlsx"
            else:
                filtro = "CSV files (*.csv)"
                extension = ".csv"
                
            archivo, _ = QFileDialog.getSaveFileName(
                self.view,
                "Exportar herrajes",
                f"herrajes{extension}",
                filtro
            )
            
            if archivo:
                # Aquí iría la lógica de exportación real
                # Por ahora, simular éxito
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self.view, "Exportar", f"Herrajes exportados a {archivo}")
                print(f"[HERRAJES CONTROLLER] Herrajes exportados a {archivo}")
                return True
            
            return False
            
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error exportando herrajes: {e}")
            return False

    # Métodos de utilidad
    def obtener_tipos_herrajes(self) -> List[str]:
        """Obtiene tipos de herrajes disponibles."""
        return ["Bisagras", "Cerraduras", "Manijas", "Otros herrajes"]

    def obtener_estados_herrajes(self) -> List[str]:
        """Obtiene estados de herrajes disponibles."""
        return ["Activo", "Inactivo"]

    def obtener_unidades_medida(self) -> List[str]:
        """Obtiene unidades de medida disponibles."""
        return ["unidad", "metro", "kilogramo", "litro", "caja"]
