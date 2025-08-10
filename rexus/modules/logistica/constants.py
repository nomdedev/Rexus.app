"""
Constantes para el módulo de Logística

Centraliza todas las constantes usadas en el módulo para facilitar el mantenimiento.
"""

from typing import Dict, List

# Tipos de servicio disponibles
TIPOS_SERVICIO: List[str] = [
    "Entrega Domicilio",
    "Transporte Obra", 
    "Servicio Express",
    "Carga Pesada",
    "Servicio Programado"
]

# Estados de entrega
ESTADOS_ENTREGA: List[str] = [
    "Todos",
    "Programada", 
    "En Tránsito",
    "Entregada",
    "Cancelada"
]

# Filtros del mapa
FILTROS_MAPA: List[str] = [
    "Todos los Servicios",
    "Solo Entregas",
    "Solo Transporte",
    "Servicios Express"
]

# Configuración de UI
UI_CONFIG = {
    "widget_widths": {
        "search_input": 140,
        "combo_estado": 100,
        "combo_tipo_servicio": 140,
        "input_cliente": 200,
        "input_direccion": 250,
        "date_programada": 110,
        "input_hora": 70,
        "input_contacto": 140
    },
    "heights": {
        "text_observaciones": 60,
        "button_height": 20,
        "table_column_id": 40
    },
    "spacing": {
        "main_layout": 8,
        "main_margins": 10,
        "tab_padding": "6px 12px",
        "groupbox_margins": 5
    }
}

# Headers de tabla
TABLE_HEADERS = {
    "entregas": ["ID", "Fecha Programada", "Dirección", "Estado", "Contacto", "Observaciones", "Acciones"],
    "servicios": ["Tipo", "Cliente", "Dirección", "Fecha", "Estado", "Acciones"],
    "transportes": ["Código", "Tipo", "Proveedor", "Disponible", "Acciones"]
}

# Mensajes de usuario
MESSAGES = {
    "success": {
        "servicio_creado": "Servicio creado para {cliente}",
        "formulario_limpio": "Formulario limpiado correctamente",
        "marcador_agregado": "Marcador agregado al mapa"
    },
    "errors": {
        "crear_servicio": "Error creando servicio desde mapa: {error}",
        "agregar_marcador": "Error agregando marcador: {error}",
        "datos_invalidos": "Por favor complete todos los campos requeridos"
    },
    "info": {
        "cobertura_zonas": "Zona Centro: La Plata centro, Tolosa, Ringuelet",
        "placeholder_mapa": "Mapa no disponible - modo desarrollo"
    }
}

# Iconos y emojis para UI
ICONS = {
    "buttons": {
        "nueva_entrega": "➕",
        "generar_servicio": "✨", 
        "limpiar": "🧹",
        "agregar_marcador": "📍",
        "info": "ℹ️",
        "retry": "🔄"
    },
    "tabs": {
        "entregas": "📦",
        "servicios": "🚛", 
        "mapa": "🗺️",
        "estadisticas": "📊"
    },
    "estados": {
        "programada": "⏰",
        "en_transito": "🚛",
        "entregada": "✅",
        "cancelada": "❌"
    }
}

# Información de cobertura para tooltips
COBERTURA_INFO = {
    "zonas": [
        {"nombre": "Zona Centro", "areas": "La Plata centro, Tolosa, Ringuelet"},
        {"nombre": "Zona Norte", "areas": "Gonnet, City Bell, Villa Elisa"},
        {"nombre": "Zona Este", "areas": "Berisso, zonas industriales"},
        {"nombre": "Zona Sur", "areas": "Los Hornos, Melchor Romero"}, 
        {"nombre": "Zona Oeste", "areas": "Ensenada, puerto"}
    ],
    "servicios": [
        {"tipo": "Entrega Express", "tiempo": "30-60 minutos (zona centro)"},
        {"tipo": "Entrega Estándar", "tiempo": "60-120 minutos (todas las zonas)"},
        {"tipo": "Transporte de Obra", "tiempo": "Coordinado según disponibilidad"},
        {"tipo": "Carga Pesada", "tiempo": "Servicios especiales para materiales grandes"}
    ]
}