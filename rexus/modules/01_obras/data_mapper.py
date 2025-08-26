"""
Mapeo centralizado de datos para obras.
Evita índices hardcodeados y facilita mantenimiento.
"""


import logging
logger = logging.getLogger(__name__)

from typing import Dict, Any, Tuple, List
from datetime import datetime


class ObrasDataMapper:
    """Mapea datos de obras entre diferentes formatos."""

    # Índices de la estructura real de la base de datos
    INDICES_BD = {
        'id': 0,
        'nombre': 1,
        'descripcion': 26,
        'codigo': 20,
        'cliente': 5,
        'fecha_inicio': 22,
        'fecha_fin_estimada': 23,
        'estado': 6,
        'presupuesto_inicial': 24,
        'responsable': 21
    }

    # Índices de las columnas de la tabla UI
    INDICES_TABLA = {
        'codigo': 0,
        'nombre': 1,
        'cliente': 2,
        'responsable': 3,
        'fecha_inicio': 4,
        'fecha_fin': 5,
        'estado': 6,
        'presupuesto': 7,
        'acciones': 8
    }

    @classmethod
    def tupla_a_dict(cls, tupla_obra: Tuple) -> Dict[str, Any]:
        """Convierte una tupla de la BD a diccionario estructurado."""
        if not tupla_obra:
            return {}

        try:
            return {
                'id': cls._extraer_campo(tupla_obra, 'id'),
                'codigo': cls._extraer_campo(tupla_obra, 'codigo'),
                'nombre': cls._extraer_campo(tupla_obra, 'nombre'),
                'descripcion': cls._extraer_campo(tupla_obra, 'descripcion'),
                'cliente': cls._extraer_campo(tupla_obra, 'cliente'),
                'fecha_inicio': cls._formatear_fecha(cls._extraer_campo(tupla_obra, 'fecha_inicio')),
                'fecha_fin_estimada': cls._formatear_fecha(cls._extraer_campo(tupla_obra, 'fecha_fin_estimada')),
                'estado': cls._extraer_campo(tupla_obra, 'estado'),
                'presupuesto_inicial': cls._formatear_presupuesto(cls._extraer_campo(tupla_obra, 'presupuesto_inicial')),
                'responsable': cls._extraer_campo(tupla_obra, 'responsable')
            }
        except Exception as e:
            logger.info(f"[MAPPER] Error mapeando tupla: {e}")
            return cls._dict_vacio()

    @classmethod
    def lista_tuplas_a_dicts(cls, tuplas_obras: List[Tuple]) -> List[Dict[str, Any]]:
        """Convierte una lista de tuplas a lista de diccionarios."""
        if not tuplas_obras:
            return []

        return [cls.tupla_a_dict(tupla) for tupla in tuplas_obras]

    @classmethod
    def dict_a_fila_tabla(cls, obra_dict: Dict[str, Any]) -> List[str]:
        """Convierte un diccionario de obra a lista para mostrar en tabla."""
        try:
            return [
                str(obra_dict.get('codigo', '')),
                str(obra_dict.get('nombre', '')),
                str(obra_dict.get('cliente', '')),
                str(obra_dict.get('responsable', '')),
                cls._formatear_fecha_tabla(obra_dict.get('fecha_inicio', '')),
                cls._formatear_fecha_tabla(obra_dict.get('fecha_fin_estimada', '')),
                str(obra_dict.get('estado', '')),
                cls._formatear_presupuesto_tabla(obra_dict.get('presupuesto_inicial', 0))
            ]
        except Exception as e:
            logger.info(f"[MAPPER] Error convirtiendo a fila: {e}")
            return [''] * 8

    @classmethod
    def _extraer_campo(cls, tupla: Tuple, campo: str) -> Any:
        """Extrae un campo de la tupla usando el índice correcto."""
        indice = cls.INDICES_BD.get(campo)
        if indice is None:
            return ''

        if len(tupla) > indice:
            valor = tupla[indice]
            return valor if valor is not None else ''
        return ''

    @classmethod
    def _formatear_fecha(cls, fecha) -> str:
        """Formatea una fecha para almacenamiento."""
        if not fecha:
            return ''

        if isinstance(fecha, str):
            # Ya es string, verificar formato
            return fecha[:10] if len(fecha) >= 10 else fecha

        if hasattr(fecha, 'strftime'):
            return fecha.strftime('%Y-%m-%d')

        return str(fecha)

    @classmethod
    def _formatear_fecha_tabla(cls, fecha) -> str:
        """Formatea una fecha para mostrar en tabla."""
        fecha_formateada = cls._formatear_fecha(fecha)
        if not fecha_formateada:
            return ''

        try:
            # Convertir a formato más legible si es necesario
            if '-' in fecha_formateada and len(fecha_formateada) == 10:
                return fecha_formateada  # Ya está en formato YYYY-MM-DD
            return fecha_formateada
        except (TypeError, AttributeError, ValueError) as e:
            logger.warning(f"Error formateando fecha para tabla: {e}")
            return str(fecha)

    @classmethod
    def _formatear_presupuesto(cls, presupuesto) -> float:
        """Formatea un presupuesto para almacenamiento."""
        if not presupuesto:
            return 0.0

        try:
            return float(presupuesto)
        except (ValueError, TypeError):
            return 0.0

    @classmethod
    def _formatear_presupuesto_tabla(cls, presupuesto) -> str:
        """Formatea un presupuesto para mostrar en tabla."""
        presupuesto_num = cls._formatear_presupuesto(presupuesto)
        if presupuesto_num == 0:
            return ''

        try:
            return f"${presupuesto_num:,.2f}"
        except (ValueError, TypeError, OverflowError) as e:
            logger.warning(f"Error formateando presupuesto para tabla: {e}")
            return str(presupuesto)

    @classmethod
    def _dict_vacio(cls) -> Dict[str, Any]:
        """Retorna un diccionario vacío con la estructura correcta."""
        return {
            'id': '',
            'codigo': '',
            'nombre': '',
            'descripcion': '',
            'cliente': '',
            'fecha_inicio': '',
            'fecha_fin_estimada': '',
            'estado': '',
            'presupuesto_inicial': 0.0,
            'responsable': ''
        }

    @classmethod
    def validar_estructura_dict(cls, obra_dict: Dict[str, Any]) -> bool:
        """Valida que un diccionario tenga la estructura correcta."""
        campos_requeridos = [
            'id', 'codigo', 'nombre', 'cliente',
            'estado', 'responsable'
        ]

        return all(campo in obra_dict for campo in campos_requeridos)


class ObrasTableHelper:
    """Helper para operaciones específicas de la tabla de obras."""

    @staticmethod
    def configurar_headers_tabla(tabla):
        """Configura los headers de la tabla de obras."""
        headers = [
            "Código", "Nombre", "Cliente", "Responsable",
            "Fecha Inicio", "Fecha Fin", "Estado", "Presupuesto", "Acciones"
        ]
        tabla.setHorizontalHeaderLabels(headers)

        # Configurar anchos de columna
        if tabla.horizontalHeader():
            header = tabla.horizontalHeader()
            header.setStretchLastSection(True)
            header.resizeSection(0, 120)  # Código
            header.resizeSection(1, 200)  # Nombre
            header.resizeSection(2, 150)  # Cliente
            header.resizeSection(3, 150)  # Responsable
            header.resizeSection(4, 100)  # Fecha Inicio
            header.resizeSection(5, 100)  # Fecha Fin
            header.resizeSection(6, 100)  # Estado
            header.resizeSection(7, 120)  # Presupuesto

    @staticmethod
    def crear_boton_accion(texto: str, callback, fila: int):
        """Crea un botón de acción para una fila específica."""
        from PyQt6.QtWidgets import QPushButton

        btn = QPushButton(texto)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn.clicked.connect(lambda: callback(fila))
        return btn


class ObrasValidator:
    """Validador de datos de obras."""

    @staticmethod
    def validar_obra_dict(obra_dict: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Valida un diccionario de obra y retorna errores si los hay."""
        errores = []

        # Validar campos requeridos
        if not obra_dict.get('nombre', '').strip():
            errores.append("El nombre es requerido")

        if not obra_dict.get('codigo', '').strip():
            errores.append("El código es requerido")

        if not obra_dict.get('cliente', '').strip():
            errores.append("El cliente es requerido")

        if not obra_dict.get('responsable', '').strip():
            errores.append("El responsable es requerido")

        # Validar formato de fechas
        fecha_inicio = obra_dict.get('fecha_inicio', '')
        if fecha_inicio and \
            not ObrasValidator._validar_formato_fecha(fecha_inicio):
            errores.append("Formato de fecha de inicio inválido")

        fecha_fin = obra_dict.get('fecha_fin_estimada', '')
        if fecha_fin and not ObrasValidator._validar_formato_fecha(fecha_fin):
            errores.append("Formato de fecha de fin inválido")

        # Validar presupuesto
        presupuesto = obra_dict.get('presupuesto_inicial', 0)
        if presupuesto and presupuesto < 0:
            errores.append("El presupuesto no puede ser negativo")

        return len(errores) == 0, errores

    @staticmethod
    def _validar_formato_fecha(fecha_str: str) -> bool:
        """Valida que una fecha tenga formato correcto."""
        if not fecha_str:
            return True  # Fecha vacía es válida

        try:
            if len(fecha_str) >= 10:
                datetime.strptime(fecha_str[:10], '%Y-%m-%d')
                return True
        except ValueError:
            pass

        return False
