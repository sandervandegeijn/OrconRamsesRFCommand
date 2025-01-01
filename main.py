
from orcon_ramses_rf_command import OrconRamsesRFCommand
from mqtt_client import MQTTClient
import time
import logging
import sys

logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for demonstration. 
    Instantiates the OrconHRC400 class and prints messages for 
    different fan speed settings.
    """
    # Create an instance with default addresses
    orcon = OrconRamsesRFCommand(remote_address="37:1111111", wtw_address="32:2222222", capacity_in_m3_per_hour=400)

    mqtt_client = MQTTClient(
        server="192.168.2.35",
        port=1883,  # Replace with your MQTT server port
        topic="RAMSES/GATEWAY/18:129404/tx",
        tls=False  # Set to True if using TLS
    )

    try:
        # Connect to MQTT broker
        mqtt_client.connect()
        
        # Give some time to establish the connection
        time.sleep(1)

        # Example 2: Set fan speed to low with 50%
        commands = orcon.set_fan_speed("low", 104)
        commands += orcon.set_to_low_mode()

        logger.debug(f"Commands:")
        
        for cmd in commands:
            logger.debug(cmd)
            mqtt_client.publish_command(cmd)
            time.sleep(1)
    
    finally:
        # Disconnect from MQTT broker
        mqtt_client.disconnect()


if __name__ == "__main__":
    log_level = "DEBUG"
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    logging.basicConfig(level=numeric_level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        stream=sys.stdout)
    main()
