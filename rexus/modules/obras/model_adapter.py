"""
Adapter para el modelo de obras que facilita testing y desacoplamiento.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric


class ObrasModelInterface(ABC):
    """Interface para el modelo de obras."""
    
    @abstractmethod
    def obtener_todas_obras(self) -> List[Tuple]:
        """Obtiene todas las obras."""
        pass
    
    @abstractmethod
    def obtener_obra_por_id(self, obra_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una obra por ID."""
        pass
    
    @abstractmethod
    def crear_obra(self, datos_obra: Dict[str, Any]) -> bool:
        """Crea una nueva obra."""
        pass
    
    @abstractmethod
    def actualizar_obra(self, obra_id: int, datos: Dict[str, Any]) -> bool:
        """Actualiza una obra existente."""
        pass
    
    @abstractmethod
    def eliminar_obra(self, obra_id: int) -> bool:
        """Elimina una obra."""
        pass
    
    @abstractmethod
    def obtener_obras_filtradas(self, filtros: Dict[str, Any]) -> List[Tuple]:
        """Obtiene obras con filtros aplicados."""
        pass


class ObrasModelAdapter(ObrasModelInterface):
    """Adapter que envuelve el modelo real de obras."""
    
    def __init__(self, modelo_real):
        """Inicializa el adapter con el modelo real."""
        self._modelo = modelo_real
    
    def obtener_todas_obras(self) -> List[Tuple]:
        """Obtiene todas las obras."""
        if not self._modelo:
            return []
        return self._modelo.obtener_todas_obras()
    
    def obtener_obra_por_id(self, obra_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una obra por ID."""
        if not self._modelo:
            return None
        return self._modelo.obtener_obra_por_id(obra_id)
    
    def crear_obra(self, datos_obra: Dict[str, Any]) -> bool:
        """Crea una nueva obra."""
        if not self._modelo:
            return False
        return self._modelo.crear_obra(datos_obra)
    
    def actualizar_obra(self, obra_id: int, datos: Dict[str, Any]) -> bool:
        """Actualiza una obra existente."""
        if not self._modelo:
            return False
        return self._modelo.actualizar_obra(obra_id, datos)
    
    def eliminar_obra(self, obra_id: int) -> bool:
        """Elimina una obra."""
        if not self._modelo:
            return False
        return self._modelo.eliminar_obra(obra_id)
    
    def obtener_obras_filtradas(self, filtros: Dict[str, Any]) -> List[Tuple]:
        """Obtiene obras con filtros aplicados."""
        if not self._modelo:
            return []
        return self._modelo.obtener_obras_filtradas(filtros)


class MockObrasModel(ObrasModelInterface):
    """Mock del modelo de obras para testing."""
    
    def __init__(self):
        """Inicializa el mock con datos de prueba."""
        self._obras = [
            (1, "Edificio Central", "DESC001", "Construcción principal", 1, 
             "2024-01-15", "2024-12-15", None, "EN_PROCESO", "Activo", 
             25.5, 150000.0, 45000.0, 15.5, "Centro", "Juan Pérez", 
             "En proceso", 1, "2024-01-10", "2024-02-15", "OBR-001", 
             "Juan Pérez", "2024-01-15", "2024-12-15", 150000.0, None, 
             "Construcción de edificio principal"),
            (2, "Plaza Comercial", "DESC002", "Centro comercial", 2, 
             "2024-02-01", "2025-01-30", None, "PLANIFICACION", "Activo", 
             60.0, 250000.0, 120000.0, 12.0, "Norte", "María García", 
             "Sin observaciones", 1, "2024-01-20", "2024-03-01", "OBR-002", 
             "María García", "2024-02-01", "2025-01-30", 250000.0, None, 
             "Centro comercial fase 1")
        ]
    
    def obtener_todas_obras(self) -> List[Tuple]:
        """Obtiene todas las obras mock."""
        return self._obras.copy()
    
    def obtener_obra_por_id(self, obra_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una obra por ID."""
        for obra in self._obras:
            if obra[0] == obra_id:
                return {
                    'id': obra[0],
                    'nombre': obra[1],
                    'codigo': obra[20] if len(obra) > 20 else f"OBR-{obra[0]:03d}",
                    'cliente': obra[5] if len(obra) > 5 else "Cliente Test",
                    'estado': obra[8] if len(obra) > 8 else "EN_PROCESO"
                }
        return None
    
    def crear_obra(self, datos_obra: Dict[str, Any]) -> bool:
        """Crea una nueva obra mock."""
        nuevo_id = max(obra[0] for obra in self._obras) + 1 if self._obras else 1
        nueva_obra = (nuevo_id, datos_obra.get('nombre', 'Nueva Obra'), 
                     f"DESC{nuevo_id:03d}", "Descripción test", nuevo_id,
                     "2024-01-01", "2024-12-31", None, "PLANIFICACION", "Activo",
                     0.0, 100000.0, 0.0, 0.0, "Ubicación Test", "Responsable Test",
                     "Nueva obra", 1, "2024-01-01", "2024-01-01", f"OBR-{nuevo_id:03d}",
                     "Responsable Test", "2024-01-01", "2024-12-31", 100000.0, None,
                     datos_obra.get('descripcion', 'Descripción test'))
        self._obras.append(nueva_obra)
        return True
    
    def actualizar_obra(self, obra_id: int, datos: Dict[str, Any]) -> bool:
        """Actualiza una obra mock."""
        for i, obra in enumerate(self._obras):
            if obra[0] == obra_id:
                # Actualizar obra (simplificado para mock)
                obra_actualizada = list(obra)
                obra_actualizada[1] = datos.get('nombre', obra[1])
                self._obras[i] = tuple(obra_actualizada)
                return True
        return False
    
    def eliminar_obra(self, obra_id: int) -> bool:
        """Elimina una obra mock."""
        for i, obra in enumerate(self._obras):
            if obra[0] == obra_id:
                del self._obras[i]
                return True
        return False
    
    def obtener_obras_filtradas(self, filtros: Dict[str, Any]) -> List[Tuple]:
        """Obtiene obras filtradas mock."""
        obras_filtradas = self._obras.copy()
        
        if filtros.get('estado') and filtros['estado'] != 'Todos':
            obras_filtradas = [obra for obra in obras_filtradas 
                             if obra[8] == filtros['estado']]
        
        return obras_filtradas
