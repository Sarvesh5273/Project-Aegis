import socket

def assert_air_gapped():
    """
    Enforces physical network isolation (Layer 0).
    If a connection to public DNS succeeds, the app hard-crashes.
    """
    try:
        # socket.create_connection safely instantiates and connects
        socket.create_connection(("8.8.8.8", 53), timeout=1)
        
        # If the above line succeeds, we are online. Kill the session.
        raise RuntimeError("NETWORK DETECTED. Aegis terminated.")
        
    except OSError:
        # Expected behavior. Connection failed = offline and secure.
        pass