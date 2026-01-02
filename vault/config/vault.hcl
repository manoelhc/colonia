# OpenBao/Vault Configuration File
# This configuration works with both OpenBao and HashiCorp Vault

# The 'storage' stanza configures where the server stores its data.
# The 'file' backend is simple and good for development/testing.
storage "file" {
  path = "/openbao/data"
}

# The 'listener' stanza defines the address and port for client requests.
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 1 # Disables TLS for simplicity in a local environment
}

# Enables the web user interface
ui = true

# (Optional) Disables mlock, which is useful for environments like macOS
# or systems where you cannot grant the necessary permission for memory locking.
disable_mlock = true

# (Optional) Sets the address that clients will use to communicate with the server
api_addr = "http://127.0.0.1:8200"