# Constantes para el módulo de Logística
# Reduce la duplicación de literales y mejora la mantenibilidad

class LogisticaConstants:
    """Constantes para el módulo de Logística"""

    # Mensajes de estado
    TABLA_NO_DISPONIBLE = "Tabla de transportes no disponible"
    ESTADO_TRANSITO = "En tránsito"
    ETIQUETA_ESTADO = "Estado:"
    VALIDACION = "Validación"

    # Ubicaciones
    ALMACEN_CENTRAL = "Almacén Central"
    SUCURSAL_NORTE = "Sucursal Norte"
    DEPOSITO_SUR = "Depósito Sur"
    CENTRO_DISTRIBUCION = "Centro Distribución"

    # Direcciones
    DIRECCION_ALMACEN_CENTRAL = "Calle 7 entre 47 y 48, La Plata"
    DIRECCION_SUCURSAL_NORTE = "Av. 13 y 44, La Plata"
    DIRECCION_DEPOSITO_SUR = "Calle 120 y 610, La Plata"
    DIRECCION_CENTRO = "Av. 1 y 60, La Plata"

    # Ciudades
    CIUDAD_BUENOS_AIRES = "Buenos Aires"
    CIUDAD_LA_PLATA = "La Plata"

    # Archivos
    EXTENSION_HTML = ".html"

    # Botones
    BOTON_EDITAR = "✏️ Editar"

    # UI Constants
    MIN_WEBVIEW_HEIGHT = 400
    DIALOG_MIN_WIDTH = 400
    FONT_SIZE_SMALL = "10px"
    PADDING_SMALL = "4px"

    # Estilos repetidos
    CARD_STYLE = """
        background-color: #fafbfc;
        border: 1px solid #e1e4e8;
        border-radius: 4px;
        padding: 6px 8px;
        min-width: 80px;
        max-width: 120px;
    """

    TITLE_LABEL_STYLE = """
        QLabel {
            font-size: 10px;
            color: #6c757d;
            font-weight: 500;
        }
    """
