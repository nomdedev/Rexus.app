"""
MIT License

Copyright (c) 2024 Rexus.app

Integración de Inventario para el Módulo de Compras
Maneja la sincronización entre compras y el sistema de inventario
"""

import logging
                        return False

        integration = get_inventory_integration(compras_db, inventario_db)
        return integration.procesar_recepcion_completa(orden_id, items_recibidos)

    except Exception as e:
