import socket
import logging

def assert_air_gapped():
    """
    Enforces physical network isolation (Layer 0 Dead-Man's Switch).
    
    Project Aegis is designed for zero-trust environments (e.g., investigative 
    journalism in hostile regimes). To guarantee that no sensitive document 
    data can be exfiltrated via background telemetry or API leaks, the application 
    actively verifies that the host machine is completely severed from the public internet.
    
    If a connection to public DNS (8.8.8.8) succeeds, the application assumes 
    the operational environment is compromised and hard-crashes immediately.
    
    Raises:
        RuntimeError: If an active internet connection is detected.
    """
    try:
        # socket.create_connection safely instantiates and connects.
        # We use Google's public DNS as a reliable, globally available ping target.
        socket.create_connection(("8.8.8.8", 53), timeout=1)
        
        # If the above line succeeds, the machine is online. We pull the plug.
        logging.critical("SECURITY VIOLATION: Active network connection detected.")
        raise RuntimeError(
            "NETWORK DETECTED. Aegis terminated to prevent data exfiltration. "
            "For your physical security, please disable Wi-Fi and Ethernet before processing documents."
        )
        
    except OSError:
        # Expected behavior. Connection failed = offline and secure.
        logging.info("Layer 0 Check Passed: System is air-gapped.")
        pass