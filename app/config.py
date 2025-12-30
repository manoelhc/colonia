"""Configuration file management for Colonia."""

import os
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

CONFIG_FILE_PATH = "/usr/local/etc/colonia/config.yml"


def ensure_config_directory():
    """Ensure the configuration directory exists."""
    config_dir = os.path.dirname(CONFIG_FILE_PATH)
    Path(config_dir).mkdir(parents=True, exist_ok=True)


def read_config() -> Dict[str, Any]:
    """Read the configuration file.
    
    Returns:
        Dictionary containing the configuration. Returns empty dict if file doesn't exist.
    """
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r') as f:
                config = yaml.safe_load(f)
                return config if config else {}
        return {}
    except Exception as e:
        logger.error(f"Error reading config file: {e}", exc_info=True)
        return {}


def write_config(config: Dict[str, Any]) -> bool:
    """Write the configuration file.
    
    Args:
        config: Dictionary containing the configuration to write.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        ensure_config_directory()
        with open(CONFIG_FILE_PATH, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        logger.error(f"Error writing config file: {e}", exc_info=True)
        return False


def get_vault_config() -> Optional[Dict[str, str]]:
    """Get Vault configuration from the config file.
    
    Returns:
        Dictionary with Vault configuration or None if not configured.
    """
    config = read_config()
    return config.get('vault')


def set_vault_config(vault_url: str, vault_token: str, vault_namespace: Optional[str] = None) -> bool:
    """Set Vault configuration in the config file.
    
    Args:
        vault_url: The URL of the Vault server
        vault_token: The authentication token for Vault
        vault_namespace: Optional namespace for Vault Enterprise
        
    Returns:
        True if successful, False otherwise.
    """
    config = read_config()
    
    vault_config = {
        'url': vault_url,
        'token': vault_token
    }
    
    if vault_namespace:
        vault_config['namespace'] = vault_namespace
    
    config['vault'] = vault_config
    return write_config(config)
