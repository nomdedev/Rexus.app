"""
Modelo de datos para la tabla de servicios

Proporciona un modelo QAbstractTableModel para la gestión de servicios.
"""

from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from ..constants import TABLE_HEADERS


class ServiciosTableModel(QAbstractTableModel):
    """Modelo de datos para la tabla de servicios."""
    
    # Señal emitida cuando los datos cambian
    data_changed_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._data: List[Dict[str, Any]] = []
        self._headers = TABLE_HEADERS["servicios"]
        self._field_names = ["tipo_servicio", "cliente", "direccion", "fecha_programada", "estado", "acciones"]
    
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
        servicio = self._data[row]
        
        if role == Qt.ItemDataRole.DisplayRole:
            if col < len(self._field_names):
                field_name = self._field_names[col]
                if field_name == "acciones":
                    return "Ver Detalles"
                elif field_name == "fecha_programada":
                    # Combinar fecha y hora si están disponibles
                    fecha = servicio.get("programada", servicio.get("fecha_programada", ""))
                    hora = servicio.get("hora", "")
                    return f"{fecha} {hora}".strip()
                return str(servicio.get(field_name, ""))
                
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Colorear filas según el tipo de servicio
            tipo = servicio.get("tipo_servicio", "").lower()
            if "express" in tipo:
                return QColor(255, 236, 179)  # Amarillo para express
            elif "obra" in tipo:
                return QColor(179, 229, 252)  # Azul para obras
            elif "pesada" in tipo:
                return QColor(255, 205, 210)  # Rojo claro para carga pesada
            else:
                return QColor(230, 255, 230)  # Verde claro por defecto
                
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            
        elif role == Qt.ItemDataRole.ToolTipRole:
            if col < len(self._field_names):
                field_name = self._field_names[col]
                if field_name == "tipo_servicio":
                    return f"Tipo: {servicio.get(field_name, '')}"
                elif field_name == "observaciones":
                    obs = servicio.get("observaciones", "")
                    return f"Observaciones: {obs}" if obs else "Sin observaciones"
                    
        return QVariant()
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Retorna los datos del encabezado."""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self._headers):
                return self._headers[section]
                
        elif role == Qt.ItemDataRole.FontRole and orientation == Qt.Orientation.Horizontal:
            font = QFont()
            font.setBold(True)
            return font
            
        return QVariant()
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Retorna las flags para el índice especificado."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
            
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        
        # La columna de acciones es clickeable
        if index.column() == len(self._field_names) - 1:
            flags |= Qt.ItemFlag.ItemIsEditable
            
        return flags
    
    def get_servicio(self, row: int) -> Optional[Dict[str, Any]]:
        """Retorna el servicio en la fila especificada."""
        if 0 <= row < len(self._data):
            return self._data[row].copy()
        return None
    
    def set_data(self, data: List[Dict[str, Any]]):
        """Establece todos los datos del modelo."""
        self.beginResetModel()
        self._data = data.copy()
        self.endResetModel()
        self.data_changed_signal.emit()
    
    def add_servicio(self, servicio: Dict[str, Any]):
        """Agrega un nuevo servicio."""
        row = len(self._data)
        self.beginInsertRows(QModelIndex(), row, row)
        self._data.append(servicio.copy())
        self.endInsertRows()
        self.data_changed_signal.emit()
    
    def update_servicio(self, row: int, servicio: Dict[str, Any]):
        """Actualiza un servicio existente."""
        if 0 <= row < len(self._data):
            self._data[row] = servicio.copy()
            
            top_left = self.index(row, 0)
            bottom_right = self.index(row, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right)
            self.data_changed_signal.emit()
    
    def remove_servicio(self, row: int):
        """Elimina un servicio."""
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
    
    def filter_by_tipo(self, tipo: str) -> List[int]:
        """Filtra servicios por tipo."""
        if not tipo or tipo == "Todos":
            return list(range(len(self._data)))
        
        matching_rows = []
        for row, servicio in enumerate(self._data):
            if servicio.get("tipo_servicio", "").lower() == tipo.lower():
                matching_rows.append(row)
        return matching_rows
    
    def get_all_data(self) -> List[Dict[str, Any]]:
        """Retorna todos los datos como lista."""
        return self._data.copy()
    
    def get_summary_by_tipo(self) -> Dict[str, int]:
        """Retorna un resumen de servicios por tipo."""
        summary = {}
        for servicio in self._data:
            tipo = servicio.get("tipo_servicio", "Desconocido")
            summary[tipo] = summary.get(tipo, 0) + 1
        return summary
    
    def get_today_services(self) -> List[Dict[str, Any]]:
        """Retorna los servicios programados para hoy."""
        from PyQt6.QtCore import QDate
        
        today = QDate.currentDate().toString("yyyy-MM-dd")
        today_services = []
        
        for servicio in self._data:
            fecha_programada = servicio.get("programada", servicio.get("fecha_programada", ""))
            if fecha_programada == today:
                today_services.append(servicio)
                
        return today_services