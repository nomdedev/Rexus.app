# Constantes para el módulo de Logística
# Reduce la duplicación de literales y mejora la mantenibilidad

class LogisticaConstants:
    """Constantes para el módulo de Logística"""
    
    # Mensajes
    TABLA_NO_DISPONIBLE = "Tabla de transportes no disponible"
    EDITAR_ICON = "✏️ Editar"
    ESTADO_EN_TRANSITO = "En tránsito"
    ESTADO_LABEL = "Estado:"
    VALIDACION_LABEL = "Validación"
    HTML_EXTENSION = ".html"
    
    # Ubicaciones
    ALMACEN_CENTRAL = "Almacén Central"
    ALMACEN_CENTRAL_DIRECCION = "Calle 7 entre 47 y 48, La Plata"
    SUCURSAL_NORTE = "Sucursal Norte"
    SUCURSAL_NORTE_DIRECCION = "Av. 13 y 44, La Plata"
    DEPOSITO_SUR = "Depósito Sur"
    DEPOSITO_SUR_DIRECCION = "Calle 120 y 610, La Plata"
    CENTRO_DISTRIBUCION = "Centro Distribución"
    CENTRO_DISTRIBUCION_DIRECCION = "Av. 1 y 60, La Plata"
    
    # Ciudades
    BUENOS_AIRES = "Buenos Aires"
    LA_PLATA = "La Plata"
    
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
