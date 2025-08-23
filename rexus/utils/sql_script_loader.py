"""SQL Script Loader Utility"""

import logging
from pathlib import Path

class SQLScriptLoader:
    def __init__(self, scripts_dir=None):
        if scripts_dir is None:
            # Auto-detect scripts directory relative to the project root
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent  # Go up from rexus/utils/
            scripts_dir = project_root /  / "sql"

        self.scripts_dir = Path(scripts_dir)
        self.logger = logging.getLogger(__name__)

    def load_script(self, script_name):
        """
        Load a SQL script with security validations.
        
        SECURITY NOTE: This method should only be used for loading trusted,
        pre-validated SQL templates. Direct execution of loaded scripts
        is disabled for security reasons.
        """
        try:
            # SECURITY: Validate script name to prevent path traversal
            if not script_name or '..' in script_name or '/' in script_name or '\\' in script_name:
                self.logger.error(f"SECURITY: Invalid script name detected: {script_name}")
                return None
                
            script_path = self.scripts_dir / f"{script_name}.sql"
            
            # SECURITY: Ensure the resolved path is within the scripts directory
            if not str(script_path.resolve()).startswith(str(self.scripts_dir.resolve())):
                self.logger.error(f"SECURITY: Path traversal attempt detected for: {script_name}")
                return None
                
            if script_path.exists():
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # SECURITY: Basic content validation
                    if len(content) > 100000:  # Limit to 100KB
                        self.logger.error(f"SECURITY: Script too large: {script_name}")
                        return None
                    return content
            else:
                self.logger.warning(f"Script SQL no encontrado: {script_path}")
                return None
        except Exception as e:

    def execute_script(self, cursor, script_name, params=None):
        """
        DEPRECATED: Direct script execution removed for security reasons.
        
        This method has been disabled to prevent arbitrary SQL code execution.
        Use parameterized queries directly in your models instead.
        """
        self.logger.error(f"SECURITY: Direct script execution disabled for {script_name}. Use parameterized queries instead.")
        return False

sql_script_loader = SQLScriptLoader()
