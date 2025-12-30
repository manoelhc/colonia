# The 'storage' stanza configures where Vault stores its data.
# The 'file' backend is simple and good for development/testing.
storage "file" {
  path = "/opt/vault/data"
}

# The 'listener' stanza defines the address and port for client requests.
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 1 # Disables TLS for simplicity in a local environment
}

# Enables the Vault web user interface
ui = true

# (Optional) Disables mlock, which is useful for environments like macOS
# or systems where you cannot grant the necessary permission for memory locking.
disable_mlock = true

# (Optional) Sets the address that clients will use to communicate with the Vault server
api_addr = "http://127.0.0.1:8200"