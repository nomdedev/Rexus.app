"""
Métodos adicionales para la vista optimizada de Obras
Callbacks y funcionalidades para los componentes mejorados

Fecha: 13/08/2025
"""

# Métodos que deben agregarse a ObrasModernView

def _on_obra_double_clicked(self, row: int, obra_data: dict):
    """
    Maneja el doble-click en una obra.
    
    Args:
        row: Fila clickeada
        obra_data: Datos de la obra
    """
    try:
        print(f"[OBRAS] Doble-click en obra: {obra_data.get('nombre_obra', 'Sin nombre')}")
        
        # Abrir diálogo de edición o vista detallada
        if hasattr(self, 'mostrar_dialogo_obra'):
            self.mostrar_dialogo_obra(obra_data)
        else:
            # Fallback - mostrar información básica
            from rexus.utils.message_system import show_info
            info_text = f"""
            Obra: {obra_data.get('nombre_obra', 'N/A')}
            Cliente: {obra_data.get('cliente', 'N/A')}
            Estado: {obra_data.get('estado', 'N/A')}
            Presupuesto: ${obra_data.get('presupuesto_total', 0):,.0f}
            """
            show_info(self, "Detalles de Obra", info_text)
            
    except Exception as e:
        print(f"[ERROR OBRAS] Error en doble-click: {e}")

def _on_obra_context_menu(self, row: int, obra_data: dict, menu):
    """
    Maneja el menú contextual de una obra.
    
    Args:
        row: Fila seleccionada
        obra_data: Datos de la obra
        menu: Menú contextual
    """
    try:
        # Agregar acciones específicas del módulo
        from PyQt6.QtGui import QAction
        
        # Acción para cronograma
        cronograma_action = QAction("📅 Ver en Cronograma", self)
        cronograma_action.triggered.connect(
            lambda: self._abrir_cronograma_obra(obra_data.get('id'))
        )
        menu.addAction(cronograma_action)
        
        # Acción para presupuesto
        presupuesto_action = QAction("💰 Ver Presupuesto", self)
        presupuesto_action.triggered.connect(
            lambda: self._abrir_presupuesto_obra(obra_data.get('id'))
        )
        menu.addAction(presupuesto_action)
        
        # Acción para cambiar estado
        if obra_data.get('estado') != 'FINALIZADA':
            cambiar_estado_action = QAction("🔄 Cambiar Estado", self)
            cambiar_estado_action.triggered.connect(
                lambda: self._cambiar_estado_obra(obra_data.get('id'))
            )
            menu.addAction(cambiar_estado_action)
            
    except Exception as e:
        print(f"[ERROR OBRAS] Error en menú contextual: {e}")

def _on_export_requested(self, format_type: str):
    """
    Maneja las solicitudes de exportación.
    
    Args:
        format_type: Tipo de formato ('xlsx', 'pdf', 'csv')
    """
    try:
        print(f"[OBRAS] Exportación solicitada: {format_type}")
        
        # Obtener datos actuales de la tabla
        obras_data = self.tabla_obras.current_data
        
        if not obras_data:
            from rexus.utils.message_system import show_warning
            show_warning(self, "Exportación", "No hay datos para exportar")
            return
        
        # Usar el sistema de exportación existente
        if hasattr(self, 'exportar_datos'):
            self.exportar_datos(format_type)
        else:
            # Implementación básica de exportación
            from rexus.utils.message_system import show_info
            show_info(self, "Exportación", f"Exportando {len(obras_data)} obras a formato {format_type}")
            
    except Exception as e:
        print(f"[ERROR OBRAS] Error en exportación: {e}")

def _on_refresh_requested(self):
    """Maneja las solicitudes de actualización."""
    try:
        print("[OBRAS] Actualización solicitada")
        
        # Actualizar datos desde el controlador
        if self.controller:
            self.controller.cargar_obras()
        else:
            # Recargar datos de ejemplo
            self.cargar_obras_en_tabla()
            
    except Exception as e:
        print(f"[ERROR OBRAS] Error en actualización: {e}")

def _abrir_cronograma_obra(self, obra_id: int):
    """
    Abre el cronograma para una obra específica.
    
    Args:
        obra_id: ID de la obra
    """
    try:
        # Cambiar a la pestaña de cronograma si existe
        if hasattr(self, 'tab_widget'):
            for i in range(self.tab_widget.count()):
                if "cronograma" in self.tab_widget.tabText(i).lower():
                    self.tab_widget.setCurrentIndex(i)
                    break
        
        print(f"[OBRAS] Abriendo cronograma para obra ID: {obra_id}")
        
    except Exception as e:
        print(f"[ERROR OBRAS] Error abriendo cronograma: {e}")

def _abrir_presupuesto_obra(self, obra_id: int):
    """
    Abre el presupuesto para una obra específica.
    
    Args:
        obra_id: ID de la obra
    """
    try:
        # Cambiar a la pestaña de presupuesto si existe
        if hasattr(self, 'tab_widget'):
            for i in range(self.tab_widget.count()):
                if "presupuesto" in self.tab_widget.tabText(i).lower():
                    self.tab_widget.setCurrentIndex(i)
                    break
        
        print(f"[OBRAS] Abriendo presupuesto para obra ID: {obra_id}")
        
    except Exception as e:
        print(f"[ERROR OBRAS] Error abriendo presupuesto: {e}")

def _cambiar_estado_obra(self, obra_id: int):
    """
    Abre diálogo para cambiar estado de obra.
    
    Args:
        obra_id: ID de la obra
    """
    try:
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Cambiar Estado de Obra")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # ComboBox con estados
        estado_combo = QComboBox()
        estados = ['PLANIFICACION', 'EN_PROCESO', 'PAUSADA', 'FINALIZADA', 'CANCELADA']
        estado_combo.addItems(estados)
        
        layout.addWidget(estado_combo)
        
        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nuevo_estado = estado_combo.currentText()
            print(f"[OBRAS] Cambiando estado de obra {obra_id} a {nuevo_estado}")
            
            # Aquí se llamaría al controlador para cambiar el estado
            if self.controller and hasattr(self.controller, 'cambiar_estado_obra'):
                self.controller.cambiar_estado_obra(obra_id, nuevo_estado)
        
    except Exception as e:
        print(f"[ERROR OBRAS] Error cambiando estado: {e}")

def actualizar_etiquetas_mejoradas(self):
    """Actualiza todas las etiquetas con componentes mejorados."""
    try:
        # Buscar y reemplazar etiquetas básicas con componentes mejorados
        widgets_to_update = []
        
        # Recorrer todos los widgets hijos
        for widget in self.findChildren(QLabel):
            # Identificar etiquetas que pueden mejorarse
            text = widget.text()
            parent_name = widget.parent().objectName() if widget.parent() else ""
            
            # Etiquetas de encabezado
            if any(keyword in text.lower() for keyword in ['obras', 'cronograma', 'presupuesto']):
                widgets_to_update.append({
                    'widget': widget,
                    'type': 'header',
                    'text': text
                })
            # Etiquetas de estado
            elif any(keyword in text.upper() for keyword in ['EN_PROCESO', 'FINALIZADA', 'PAUSADA']):
                widgets_to_update.append({
                    'widget': widget,
                    'type': 'status',
                    'text': text
                })
            # Etiquetas de métricas (con números o $)
            elif any(char in text for char in ['$', '%']) or text.replace(',', '').replace('.', '').isdigit():
                widgets_to_update.append({
                    'widget': widget,
                    'type': 'metric',
                    'text': text
                })
        
        # Actualizar widgets identificados
        updated_count = 0
        for item in widgets_to_update:
            try:
                widget = item['widget']
                widget_type = item['type']
                text = item['text']
                
                # Crear etiqueta mejorada
                if widget_type == 'header':
                    enhanced_label = EnhancedLabel(text, 'header', widget.parent())
                elif widget_type == 'status':
                    enhanced_label = StatusIndicatorLabel(widget.parent())
                    enhanced_label.set_obra_status(text)
                elif widget_type == 'metric':
                    enhanced_label = MetricDisplayLabel('general', widget.parent())
                    enhanced_label.setText(text)
                else:
                    enhanced_label = EnhancedLabel(text, 'default', widget.parent())
                
                # Reemplazar en el layout
                parent_layout = widget.parent().layout()
                if parent_layout:
                    # Encontrar posición del widget original
                    for i in range(parent_layout.count()):
                        if parent_layout.itemAt(i).widget() == widget:
                            # Remover widget original
                            parent_layout.removeWidget(widget)
                            widget.deleteLater()
                            
                            # Insertar widget mejorado
                            parent_layout.insertWidget(i, enhanced_label)
                            updated_count += 1
                            break
                            
            except Exception as e:
                print(f"[ERROR OBRAS] Error actualizando widget: {e}")
                continue
        
        print(f"[OBRAS] Actualizadas {updated_count} etiquetas con componentes mejorados")
        
    except Exception as e:
        print(f"[ERROR OBRAS] Error actualizando etiquetas: {e}")


# Método para aplicar tema dinámico
def aplicar_tema_dinamico(self, dark_mode: bool = False):
    """
    Aplica tema dinámico a todos los componentes mejorados.
    
    Args:
        dark_mode: True para tema oscuro
    """
    try:
        # Aplicar tema a tabla optimizada
        if hasattr(self, 'tabla_obras') and hasattr(self.tabla_obras, 'apply_theme'):
            self.tabla_obras.apply_theme(dark_mode)
        
        # Aplicar tema a etiquetas mejoradas
        enhanced_labels = self.findChildren(EnhancedLabel)
        for label in enhanced_labels:
            if hasattr(label, 'set_theme'):
                label.set_theme(dark_mode)
        
        # Aplicar tema a indicadores de estado
        status_labels = self.findChildren(StatusIndicatorLabel)
        for label in status_labels:
            if hasattr(label, 'set_theme'):
                label.set_theme(dark_mode)
        
        # Aplicar tema a métricas
        metric_labels = self.findChildren(MetricDisplayLabel)
        for label in metric_labels:
            if hasattr(label, 'set_theme'):
                label.set_theme(dark_mode)
        
        print(f"[OBRAS] Tema {'oscuro' if dark_mode else 'claro'} aplicado a componentes mejorados")
        
    except Exception as e:
        print(f"[ERROR OBRAS] Error aplicando tema: {e}")