"""
Modelo de datos para la tabla de entregas

Proporciona un modelo QAbstractTableModel para mejor gestión de los datos.
"""

from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant, pyqtSignal
from PyQt6.QtGui import QColor

from ..constants import TABLE_HEADERS


class EntregasTableModel(QAbstractTableModel):
    """Modelo de datos para la tabla de entregas."""
    
    # Señal emitida cuando los datos cambian
    data_changed_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._data: List[Dict[str, Any]] = []
        self._headers = TABLE_HEADERS["entregas"]
        self._field_names = ["id", "fecha_programada", "direccion", "estado", "contacto", "observaciones", "acciones"]
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Retorna el número de filas."""
        return len(self._data)
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Retorna el número de columnas."""
        return len(self._headers)
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Retorna los datos para el índice y rol especificados."""
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return QVariant()
        
        row = index.row()
        col = index.column()
        entrega = self._data[row]
        
        if role == Qt.ItemDataRole.DisplayRole:
            if col < len(self._field_names):
                field_name = self._field_names[col]
                if field_name == "acciones":
                    return "Ver • Editar • Eliminar"
                return str(entrega.get(field_name, ""))
            
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Colorear filas según el estado
            estado = entrega.get("estado", "").lower()
            if estado == "entregada":
                return QColor(212, 237, 218)  # Verde claro
            elif estado == "en tránsito":
                return QColor(255, 243, 205)  # Amarillo claro  
            elif estado == "cancelada":
                return QColor(248, 215, 218)  # Rojo claro
            elif estado == "programada":
                return QColor(217, 237, 247)  # Azul claro
                
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if col == 0:  # ID column
                return Qt.AlignmentFlag.AlignCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            
        elif role == Qt.ItemDataRole.ToolTipRole:
            if col < len(self._field_names):
                field_name = self._field_names[col]
                value = entrega.get(field_name, "")
                if field_name == "observaciones" and value:
                    return f"Observaciones: {value}"
                elif field_name == "estado":
                    return f"Estado actual: {value}"
                    
        return QVariant()
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Retorna los datos del encabezado."""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self._headers):
                return self._headers[section]
                
        elif role == Qt.ItemDataRole.FontRole and orientation == Qt.Orientation.Horizontal:
            from PyQt6.QtGui import QFont
            font = QFont()
            font.setBold(True)
            return font
            
        return QVariant()
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Retorna las flags para el índice especificado."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
            
        # Solo lectura para todas las columnas excepto acciones
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        
        # La columna de acciones podría ser clickeable
        if index.column() == len(self._field_names) - 1:  # Columna acciones
            flags |= Qt.ItemFlag.ItemIsEditable
            
        return flags
    
    def get_entrega(self, row: int) -> Optional[Dict[str, Any]]:
        """Retorna la entrega en la fila especificada."""
        if 0 <= row < len(self._data):
            return self._data[row].copy()
        return None
    
    def set_data(self, data: List[Dict[str, Any]]):
        """Establece todos los datos del modelo."""
        self.beginResetModel()
        self._data = data.copy()
        self.endResetModel()
        self.data_changed_signal.emit()
    
    def add_entrega(self, entrega: Dict[str, Any]):
        """Agrega una nueva entrega."""
        row = len(self._data)
        self.beginInsertRows(QModelIndex(), row, row)
        self._data.append(entrega.copy())
        self.endInsertRows()
        self.data_changed_signal.emit()
    
    def update_entrega(self, row: int, entrega: Dict[str, Any]):
        """Actualiza una entrega existente."""
        if 0 <= row < len(self._data):
            self._data[row] = entrega.copy()
            
            # Emitir señal de cambio para toda la fila
            top_left = self.index(row, 0)
            bottom_right = self.index(row, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right)
            self.data_changed_signal.emit()
    
    def remove_entrega(self, row: int):
        """Elimina una entrega."""
        if 0 <= row < len(self._data):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._data[row]
            self.endRemoveRows()
            self.data_changed_signal.emit()
    
    def clear(self):
        """Limpia todos los datos."""
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()
        self.data_changed_signal.emit()
    
    def filter_data(self, filter_func) -> List[int]:
        """
        Filtra los datos y retorna las filas que coinciden.
        
        Args:
            filter_func: Función que toma una entrega y retorna True si coincide
            
        Returns:
            Lista de índices de filas que coinciden con el filtro
        """
        matching_rows = []
        for row, entrega in enumerate(self._data):
            if filter_func(entrega):
                matching_rows.append(row)
        return matching_rows
    
    def get_all_data(self) -> List[Dict[str, Any]]:
        """Retorna todos los datos como lista."""
        return self._data.copy()
    
    def find_by_id(self, entrega_id: int) -> Optional[int]:
        """Busca una entrega por ID y retorna su índice de fila."""
        for row, entrega in enumerate(self._data):
            if entrega.get("id") == entrega_id:
                return row
        return None
    
    def get_summary(self) -> Dict[str, int]:
        """Retorna un resumen de las entregas por estado."""
        summary = {}
        for entrega in self._data:
            estado = entrega.get("estado", "Desconocido")
            summary[estado] = summary.get(estado, 0) + 1
        return summary