
# 🔒 REPORTE DE SEGURIDAD - Rexus.app

## Resumen Ejecutivo

- **Total de issues**: 49
- **Críticos**: 22
- **Altos**: 16
- **Estado**: 🔴 CRÍTICO

## Detalles por Categoría

### Broad Exceptions

**🟡 contextual_error_system.py:483**
- Contenido: `except Exception:`
- Recomendación: Usar excepciones específicas como ValueError, TypeError, etc.

**🟡 error_notification_widget.py:347**
- Contenido: `except Exception:`
- Recomendación: Usar excepciones específicas como ValueError, TypeError, etc.

**🟡 security_clean.py:42**
- Contenido: `except Exception:`
- Recomendación: Usar excepciones específicas como ValueError, TypeError, etc.

**🟡 theme_fixes.py:140**
- Contenido: `except Exception:`
- Recomendación: Usar excepciones específicas como ValueError, TypeError, etc.

### Sql Injection Risks

**🟠 pagination.py:340**
- Contenido: `count_query = f"SELECT COUNT(*) {from_part}"`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

**🟠 pagination.py:342**
- Contenido: `count_query = f"SELECT COUNT(*) FROM ({base_query}) AS count_subquery"`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

**🟠 pagination_manager.py:147**
- Contenido: `base_query = f"SELECT COUNT(*) FROM {self.table_name} WHERE activo = 1"`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

**🟠 query_optimizer.py:176**
- Contenido: `query = f"SELECT {columns} FROM {table} WHERE id IN ({placeholders})"`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

**🟠 query_optimizer.py:547**
- Contenido: `query = f"SELECT {columns} FROM {table} WHERE id IN ({placeholders})"`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

**🟠 security_analyzer.py:105**
- Contenido: `r'f".*SELECT.*{.*}',`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

**🟠 security_analyzer.py:106**
- Contenido: `r'f".*INSERT.*{.*}',`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

**🟠 security_analyzer.py:107**
- Contenido: `r'f".*UPDATE.*{.*}',`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

**🟠 security_analyzer.py:108**
- Contenido: `r'f".*DELETE.*{.*}',`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

**🟠 sql_security.py:267**
- Contenido: `query = f"SELECT {columns_str} FROM [{safe_table}]"`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

**🟠 sql_security.py:304**
- Contenido: `return f"INSERT INTO [{safe_table}] ({columns_str}) VALUES ({placeholders})"`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

**🟠 sql_security.py:332**
- Contenido: `return f"UPDATE [{safe_table}] SET {set_clause} WHERE {where_condition}"`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

**🟠 sql_security.py:347**
- Contenido: `return f"DELETE FROM [{safe_table}] WHERE {where_condition}"`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

**🟠 sql_security.py:429**
- Contenido: `self.query_parts.append(f"SELECT {columns}")`
- Recomendación: Usar consultas parametrizadas o SQLQueryManager

### Unsafe Evals

**🔴 contextual_error_system.py:473**
- Contenido: `dialog.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 contextual_error_system.py:493**
- Contenido: `msg_box.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 dialogs.py:43**
- Contenido: `msg_box.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 dialogs.py:58**
- Contenido: `msg_box.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 dialogs.py:73**
- Contenido: `msg_box.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 dialogs.py:88**
- Contenido: `msg_box.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 dialogs.py:107**
- Contenido: `result = msg_box.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 dialog_utils.py:334**
- Contenido: `if dialog.exec() == QDialog.DialogCode.Accepted:`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 dialog_utils.py:387**
- Contenido: `if dialog.exec() == QDialog.DialogCode.Accepted:`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 error_handler.py:44**
- Contenido: `msg_box.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 error_manager.py:260**
- Contenido: `result = msg_box.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 error_manager.py:296**
- Contenido: `msg_box.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 error_manager.py:369**
- Contenido: `result = msg_box.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 error_notification_widget.py:221**
- Contenido: `details_dialog.show()  # Usar show() en lugar de exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 error_notification_widget.py:424**
- Contenido: `sys.exit(app.exec())`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 export_manager.py:382**
- Contenido: `dialog.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 feedback_manager.py:206**
- Contenido: `result = msg_box.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 feedback_manager.py:253**
- Contenido: `result = msg_box.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 keyboard_help.py:143**
- Contenido: `dialog.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 message_system.py:165**
- Contenido: `return msg_box.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 message_system.py:171**
- Contenido: `fallback_msg.exec()`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

**🔴 security_analyzer.py:132**
- Contenido: `"""Encuentra usos de eval() y exec()."""`
- Recomendación: Evitar eval/exec, usar parsing seguro o funciones específicas

### Hardcoded Secrets

**🟠 contextual_error_manager.py:55**
- Contenido: `AUTH_WEAK_PASSWORD = "AUTH_005"  # nosec B105 - Th...`
- Recomendación: Mover secrets a variables de entorno o archivos de configuración

### Insecure Patterns

**🟠 cache_manager.py:135**
- Contenido: `return pickle.loads(data)`
- Recomendación: Usar JSON u otros formatos seguros

**🟢 data_sanitizer.py:56**
- Contenido: `def sanitize_sql_input(text: Union[str, Any]) -> str:`
- Recomendación: Validar entrada del usuario

**🟢 input_validator.py:470**
- Contenido: `return input_validator.validate_input(value, field_type, field_name, kwargs)`
- Recomendación: Validar entrada del usuario

**🟢 security.py:44**
- Contenido: `def sanitize_input(user_input: str) -> str:`
- Recomendación: Validar entrada del usuario

**🟡 security_analyzer.py:185**
- Contenido: `(r'shell\s*=\s*True', 'shell_injection', 'medium', 'Evitar shell=True en subprocess'),`
- Recomendación: Evitar shell=True en subprocess

**🟢 security_clean.py:46**
- Contenido: `def sanitize_input(user_input: str) -> str:`
- Recomendación: Validar entrada del usuario

**🟢 sql_security.py:405**
- Contenido: `def sanitize_input(input_value: str) -> str:`
- Recomendación: Validar entrada del usuario

**🟢 unified_sanitizer.py:290**
- Contenido: `def sanitize_sql_input(self, value: Any) -> str:`
- Recomendación: Validar entrada del usuario


## Próximos Pasos

1. **Priorizar issues críticos y altos**
2. **Implementar fixes siguiendo las recomendaciones**
3. **Ejecutar este análisis regularmente en CI/CD**
4. **Considerar integrar herramientas como bandit para análisis continuo**

---
Generado por SecurityAnalyzer de Rexus.app
