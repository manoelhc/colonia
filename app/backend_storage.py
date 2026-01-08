"""Backend Storage utilities for S3-compatible storage (Minio, DigitalOcean Spaces, AWS S3, etc.)."""

import boto3
import logging
from typing import Tuple, Optional, List, Dict
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError
from app.vault import get_vault_client
from app.config import get_vault_config

logger = logging.getLogger(__name__)


def get_s3_client(endpoint_url: str, access_key: str, secret_key: str, region: str = "us-east-1"):
    """Create and return an S3 client configured for the given endpoint.
    
    Args:
        endpoint_url: The endpoint URL for the S3-compatible service
        access_key: AWS access key ID
        secret_key: AWS secret access key
        region: AWS region (default: us-east-1)
        
    Returns:
        boto3 S3 client
    """
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        return s3_client
    except Exception as e:
        logger.error(f"Error creating S3 client: {e}", exc_info=True)
        return None


def get_credentials_from_vault(vault_path: str, access_key_field: str, secret_key_field: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Retrieve S3 credentials from Vault.
    
    Args:
        vault_path: Path in Vault where credentials are stored
        access_key_field: Field name for the access key in Vault
        secret_key_field: Field name for the secret key in Vault
        
    Returns:
        Tuple of (access_key, secret_key, error_message)
    """
    try:
        # Get Vault configuration
        vault_config = get_vault_config()
        if not vault_config:
            return None, None, "Vault is not configured"
        
        vault_url = vault_config.get('url')
        vault_token = vault_config.get('token')
        vault_namespace = vault_config.get('namespace')
        
        if not vault_url or not vault_token:
            return None, None, "Vault URL and token are required"
        
        # Get Vault client
        client = get_vault_client(vault_url, vault_token, vault_namespace)
        if not client:
            return None, None, "Failed to authenticate with Vault"
        
        # Read secret from Vault
        # Try KV v2 first (data/ prefix)
        try:
            secret_response = client.secrets.kv.v2.read_secret_version(path=vault_path)
            secret_data = secret_response['data']['data']
        except Exception:
            # Try KV v1
            try:
                secret_response = client.secrets.kv.v1.read_secret(path=vault_path)
                secret_data = secret_response['data']
            except Exception as e:
                return None, None, f"Failed to read secret from Vault: {str(e)}"
        
        access_key = secret_data.get(access_key_field)
        secret_key = secret_data.get(secret_key_field)
        
        if not access_key or not secret_key:
            return None, None, f"Credentials not found in Vault at path {vault_path}"
        
        return access_key, secret_key, None
        
    except Exception as e:
        logger.error(f"Error retrieving credentials from Vault: {e}", exc_info=True)
        return None, None, f"Unexpected error: {str(e)}"


def test_s3_connection(
    endpoint_url: str,
    bucket_name: str,
    access_key: str,
    secret_key: str,
    region: str = "us-east-1"
) -> Tuple[bool, List[Dict[str, str]]]:
    """Test S3 connection by performing create, edit, revert, and delete operations.
    
    This performs a comprehensive test of the S3 backend:
    1. Create an object
    2. Edit the object (update)
    3. Edit the object again
    4. Revert to previous version (if versioning is enabled)
    5. Delete the object
    
    Args:
        endpoint_url: The endpoint URL for the S3-compatible service
        bucket_name: The bucket name to test against
        access_key: AWS access key ID
        secret_key: AWS secret access key
        region: AWS region (default: us-east-1)
        
    Returns:
        Tuple of (success: bool, results: List[Dict[str, str]])
        Each result contains: {"step": str, "status": "success"|"failed", "message": str}
    """
    results = []
    test_key = f"colonia-test-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
    
    try:
        # Create S3 client
        s3_client = get_s3_client(endpoint_url, access_key, secret_key, region)
        if not s3_client:
            results.append({
                "step": "Initialize S3 Client",
                "status": "failed",
                "message": "Failed to create S3 client"
            })
            return False, results
        
        results.append({
            "step": "Initialize S3 Client",
            "status": "success",
            "message": "S3 client created successfully"
        })
        
        # Step 1: Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            results.append({
                "step": "Check Bucket Access",
                "status": "success",
                "message": f"Bucket '{bucket_name}' is accessible"
            })
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                results.append({
                    "step": "Check Bucket Access",
                    "status": "failed",
                    "message": f"Bucket '{bucket_name}' does not exist"
                })
            else:
                results.append({
                    "step": "Check Bucket Access",
                    "status": "failed",
                    "message": f"Cannot access bucket '{bucket_name}': {str(e)}"
                })
            return False, results
        
        # Step 2: Create an object
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=b'Colonia backend storage test - Version 1'
            )
            results.append({
                "step": "Create Object",
                "status": "success",
                "message": f"Object '{test_key}' created successfully"
            })
        except Exception as e:
            results.append({
                "step": "Create Object",
                "status": "failed",
                "message": f"Failed to create object: {str(e)}"
            })
            return False, results
        
        # Step 3: Edit the object (first update)
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=b'Colonia backend storage test - Version 2 (First Edit)'
            )
            results.append({
                "step": "Edit Object (First Update)",
                "status": "success",
                "message": f"Object '{test_key}' updated successfully"
            })
        except Exception as e:
            results.append({
                "step": "Edit Object (First Update)",
                "status": "failed",
                "message": f"Failed to update object: {str(e)}"
            })
            # Try to clean up
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            except Exception:
                pass
            return False, results
        
        # Step 4: Edit the object again (second update)
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=b'Colonia backend storage test - Version 3 (Second Edit)'
            )
            results.append({
                "step": "Edit Object (Second Update)",
                "status": "success",
                "message": f"Object '{test_key}' updated successfully"
            })
        except Exception as e:
            results.append({
                "step": "Edit Object (Second Update)",
                "status": "failed",
                "message": f"Failed to update object: {str(e)}"
            })
            # Try to clean up
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            except Exception:
                pass
            return False, results
        
        # Step 5: Try to revert to previous version (if versioning is enabled)
        try:
            # Get object versions
            versions_response = s3_client.list_object_versions(Bucket=bucket_name, Prefix=test_key)
            versions = versions_response.get('Versions', [])
            
            if len(versions) > 1:
                # Get the second-to-last version (before the latest update)
                previous_version_id = versions[1]['VersionId']
                
                # Copy the previous version to make it the current version
                s3_client.copy_object(
                    Bucket=bucket_name,
                    CopySource={'Bucket': bucket_name, 'Key': test_key, 'VersionId': previous_version_id},
                    Key=test_key
                )
                results.append({
                    "step": "Revert to Previous Version",
                    "status": "success",
                    "message": f"Object reverted to version {previous_version_id}"
                })
            else:
                results.append({
                    "step": "Revert to Previous Version",
                    "status": "success",
                    "message": "Versioning not enabled or only one version exists (operation skipped)"
                })
        except Exception as e:
            # Versioning might not be enabled, which is acceptable
            results.append({
                "step": "Revert to Previous Version",
                "status": "success",
                "message": f"Version revert not available (versioning may not be enabled): {str(e)}"
            })
        
        # Step 6: Delete the object
        try:
            s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            results.append({
                "step": "Delete Object",
                "status": "success",
                "message": f"Object '{test_key}' deleted successfully"
            })
        except Exception as e:
            results.append({
                "step": "Delete Object",
                "status": "failed",
                "message": f"Failed to delete object: {str(e)}"
            })
            return False, results
        
        # All steps completed successfully
        return True, results
        
    except Exception as e:
        logger.error(f"Unexpected error during S3 connection test: {e}", exc_info=True)
        results.append({
            "step": "Test S3 Connection",
            "status": "failed",
            "message": f"Unexpected error: {str(e)}"
        })
        return False, results


def store_credentials_in_vault(
    vault_path: str,
    access_key: str,
    secret_key: str,
    access_key_field: str = "access_key",
    secret_key_field: str = "secret_key"
) -> Tuple[bool, str]:
    """Store S3 credentials in Vault.
    
    Args:
        vault_path: Path in Vault where credentials will be stored
        access_key: AWS access key ID
        secret_key: AWS secret access key
        access_key_field: Field name for the access key in Vault
        secret_key_field: Field name for the secret key in Vault
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Get Vault configuration
        vault_config = get_vault_config()
        if not vault_config:
            return False, "Vault is not configured"
        
        vault_url = vault_config.get('url')
        vault_token = vault_config.get('token')
        vault_namespace = vault_config.get('namespace')
        
        if not vault_url or not vault_token:
            return False, "Vault URL and token are required"
        
        # Get Vault client
        client = get_vault_client(vault_url, vault_token, vault_namespace)
        if not client:
            return False, "Failed to authenticate with Vault"
        
        # Prepare secret data
        secret_data = {
            access_key_field: access_key,
            secret_key_field: secret_key
        }
        
        # Store secret in Vault
        # Try KV v2 first
        try:
            client.secrets.kv.v2.create_or_update_secret(
                path=vault_path,
                secret=secret_data
            )
            return True, f"Credentials stored successfully in Vault at path '{vault_path}'"
        except Exception:
            # Try KV v1
            try:
                client.secrets.kv.v1.create_or_update_secret(
                    path=vault_path,
                    secret=secret_data
                )
                return True, f"Credentials stored successfully in Vault at path '{vault_path}'"
            except Exception as e:
                return False, f"Failed to store secret in Vault: {str(e)}"
        
    except Exception as e:
        logger.error(f"Error storing credentials in Vault: {e}", exc_info=True)
        return False, f"Unexpected error: {str(e)}"
