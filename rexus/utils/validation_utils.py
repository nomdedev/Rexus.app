"""
Utilidades de validación extendidas - Rexus.app v2.0.0

Proporciona validadores avanzados y reglas de negocio comunes.
"""


import logging
logger = logging.getLogger(__name__)

import re
                manager.add_field_validator("importe", lambda v: AdvancedValidator.validate_positive_number(v, "Importe"))
    manager.add_field_validator("stock_actual", lambda v: AdvancedValidator.validate_number_range(v, 0, None, "Stock actual"))
    manager.add_field_validator("stock_minimo", lambda v: AdvancedValidator.validate_number_range(v, 0, None, "Stock mínimo"))

    return manager
