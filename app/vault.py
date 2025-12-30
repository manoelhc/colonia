"""HashiCorp Vault client utilities for Colonia."""

import hvac
import requests.exceptions
from typing import Tuple, Optional


def test_vault_connection(vault_url: str, vault_token: str, vault_namespace: Optional[str] = None) -> Tuple[bool, str]:
    """Test connection and authentication to HashiCorp Vault.
    
    Args:
        vault_url: The URL of the Vault server (e.g., http://localhost:8200)
        vault_token: The authentication token for Vault
        vault_namespace: Optional namespace for Vault Enterprise
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Create Vault client
        client = hvac.Client(
            url=vault_url,
            token=vault_token,
            namespace=vault_namespace
        )
        
        # Test if client is authenticated
        if not client.is_authenticated():
            return False, "Authentication failed: Invalid token or insufficient permissions"
        
        # Try to read the token's information to verify access
        try:
            token_info = client.auth.token.lookup_self()
            policies = token_info.get('data', {}).get('policies', [])
            
            return True, f"Connection successful! Token has policies: {', '.join(policies)}"
        except hvac.exceptions.Forbidden:
            return False, "Authentication succeeded but token has insufficient permissions to lookup self"
        except hvac.exceptions.InvalidRequest as e:
            # Token lookup failed but authentication worked
            return True, "Connection and authentication successful!"
            
    except hvac.exceptions.InvalidRequest as e:
        return False, f"Invalid request: {str(e)}"
    except hvac.exceptions.Unauthorized:
        return False, "Authentication failed: Unauthorized access"
    except hvac.exceptions.VaultError as e:
        return False, f"Vault error: {str(e)}"
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: Cannot reach Vault server at {vault_url}"
    except requests.exceptions.RequestException as e:
        return False, f"Request error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def get_vault_client(vault_url: str, vault_token: str, vault_namespace: Optional[str] = None) -> Optional[hvac.Client]:
    """Get an authenticated Vault client.
    
    Args:
        vault_url: The URL of the Vault server
        vault_token: The authentication token for Vault
        vault_namespace: Optional namespace for Vault Enterprise
        
    Returns:
        Authenticated Vault client or None if connection fails
    """
    try:
        client = hvac.Client(
            url=vault_url,
            token=vault_token,
            namespace=vault_namespace
        )
        
        if client.is_authenticated():
            return client
        return None
    except Exception:
        return None


def list_secrets_engines(vault_url: str, vault_token: str, vault_namespace: Optional[str] = None) -> Tuple[bool, any]:
    """List all mounted secrets engines in Vault.
    
    Args:
        vault_url: The URL of the Vault server
        vault_token: The authentication token for Vault
        vault_namespace: Optional namespace for Vault Enterprise
        
    Returns:
        Tuple of (success: bool, data: dict or error message)
    """
    try:
        client = get_vault_client(vault_url, vault_token, vault_namespace)
        if not client:
            return False, "Failed to authenticate with Vault"
        
        # List mounted secrets engines
        secrets_engines = client.sys.list_mounted_secrets_engines()
        
        # Format the response
        engines = []
        for path, details in secrets_engines.get('data', {}).items():
            engines.append({
                'path': path.rstrip('/'),
                'type': details.get('type', 'unknown'),
                'description': details.get('description', ''),
                'options': details.get('options', {})
            })
        
        return True, engines
        
    except hvac.exceptions.Forbidden:
        return False, "Insufficient permissions to list secrets engines"
    except hvac.exceptions.VaultError as e:
        return False, f"Vault error: {str(e)}"
    except requests.exceptions.ConnectionError:
        return False, f"Connection error: Cannot reach Vault server at {vault_url}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def enable_secrets_engine(
    vault_url: str, 
    vault_token: str, 
    engine_type: str, 
    path: str,
    vault_namespace: Optional[str] = None,
    max_versions: Optional[int] = None
) -> Tuple[bool, str]:
    """Enable a secrets engine at the specified path.
    
    Args:
        vault_url: The URL of the Vault server
        vault_token: The authentication token for Vault
        engine_type: Type of secrets engine (kv, kv-v2)
        path: Path where the secrets engine will be mounted
        vault_namespace: Optional namespace for Vault Enterprise
        max_versions: Maximum number of versions to keep (KV v2 only)
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        client = get_vault_client(vault_url, vault_token, vault_namespace)
        if not client:
            return False, "Failed to authenticate with Vault"
        
        # Prepare options based on engine type
        options = {}
        description = f"Colonia secrets engine at {path}"
        
        if engine_type == 'kv-v2':
            # KV v2 uses the 'kv' type with version 2
            actual_type = 'kv'
            options = {'version': '2'}
            if max_versions:
                # Note: max_versions is set via configuration after mount
                pass
        elif engine_type == 'kv':
            # KV v1
            actual_type = 'kv'
            options = {'version': '1'}
        else:
            return False, f"Unsupported engine type: {engine_type}"
        
        # Enable the secrets engine
        client.sys.enable_secrets_engine(
            backend_type=actual_type,
            path=path,
            description=description,
            options=options
        )
        
        # Configure max_versions for KV v2
        if engine_type == 'kv-v2' and max_versions:
            try:
                client.secrets.kv.v2.configure(
                    max_versions=max_versions,
                    mount_point=path
                )
            except Exception as e:
                # Engine was enabled but configuration failed
                return True, f"Secrets engine enabled at '{path}' but failed to set max_versions: {str(e)}"
        
        return True, f"Secrets engine '{engine_type}' successfully enabled at path '{path}'"
        
    except hvac.exceptions.InvalidRequest as e:
        error_msg = str(e)
        if 'path is already in use' in error_msg.lower():
            return False, f"A secrets engine is already mounted at path '{path}'"
        return False, f"Invalid request: {error_msg}"
    except hvac.exceptions.Forbidden:
        return False, "Insufficient permissions to enable secrets engine"
    except hvac.exceptions.VaultError as e:
        return False, f"Vault error: {str(e)}"
    except requests.exceptions.ConnectionError:
        return False, f"Connection error: Cannot reach Vault server at {vault_url}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
