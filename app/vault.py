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
