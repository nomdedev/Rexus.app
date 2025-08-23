
# Importar utilidades de sanitización
                            return []
            
            # Usar SQL externo para búsqueda filtrada
            # Preparar parámetros para la consulta
            params = {
                'busqueda': filtros.get('busqueda') if filtros.get('busqueda') else None,
                'rol': filtros.get('rol') if filtros.get('rol') and filtros['rol'] != 'Todos' else None,
                'estado': filtros.get('estado') if filtros.get('estado') and filtros['estado'] != 'Todos' else None
            }
            
            # Ejecutar consulta usando SQL Manager
            usuarios = self.sql_manager.ejecutar_consulta_archivo(
                'usuarios/buscar_usuarios_filtrado.sql',
                params
            )
            
            # Convertir a lista de diccionarios si es necesario
            if usuarios and not isinstance(usuarios[0], dict):
                # Convertir tuplas a diccionarios
                columns = ['id', 'username', 'email', 'nombre_completo', 'departamento', 
                          'cargo', 'telefono', 'activo', 'fecha_creacion', 'ultimo_acceso', 'rol', 'estado']
                usuarios = [dict(zip(columns, row)) for row in usuarios]
            
            # Sanitizar datos de salida si está disponible
            if self.data_sanitizer and usuarios:
                usuarios = [self.data_sanitizer.sanitize_dict(usuario) for usuario in usuarios]
            
            logger.info(f"Filtrados {len(usuarios) if usuarios else 0} usuarios exitosamente")
            return usuarios or []
            
        except Exception as e:
