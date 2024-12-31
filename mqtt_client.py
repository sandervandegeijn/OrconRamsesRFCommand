import json
import logging
from typing import Optional

import json
import logging
from typing import Optional

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

class MQTTClient:
    """
    A class to handle MQTT connections and publish JSON-wrapped messages.
    """

    def __init__(
        self,
        server: str,
        port: int = 1883,
        topic: str = "default/topic",
        client_id: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        keepalive: int = 60,
        tls: bool = False,
        tls_ca_cert: Optional[str] = None,
        tls_certfile: Optional[str] = None,
        tls_keyfile: Optional[str] = None,
    ):
        """
        Initialize the MQTT client.

        :param server: MQTT broker address.
        :param port: MQTT broker port. Default is 1883.
        :param topic: MQTT topic to publish messages to.
        :param client_id: MQTT client ID. If None, a random ID is generated.
        :param username: Username for MQTT broker authentication.
        :param password: Password for MQTT broker authentication.
        :param keepalive: Keepalive interval in seconds. Default is 60.
        :param tls: Whether to use TLS. Default is False.
        :param tls_ca_cert: Path to CA certificate file.
        :param tls_certfile: Path to client certificate file.
        :param tls_keyfile: Path to client key file.
        """
        self.server = server
        self.port = port
        self.topic = topic
        self.client_id = client_id or f"mqtt_client_{id(self)}"
        self.username = username
        self.password = password
        self.keepalive = keepalive
        self.tls = tls
        self.tls_ca_cert = tls_ca_cert
        self.tls_certfile = tls_certfile
        self.tls_keyfile = tls_keyfile

        self.client = mqtt.Client(client_id=self.client_id)
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        if self.tls:
            if not self.tls_ca_cert:
                raise ValueError("CA certificate path must be provided for TLS.")
            self.client.tls_set(
                ca_certs=self.tls_ca_cert,
                certfile=self.tls_certfile,
                keyfile=self.tls_keyfile,
            )

        # Assign callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

        # Setup logging
        self.logger = logger

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when the client connects to the broker.

        :param client: The client instance.
        :param userdata: Private user data.
        :param flags: Response flags.
        :param rc: Connection result.
        """
        if rc == 0:
            self.logger.info(f"Connected to MQTT Broker: {self.server}:{self.port}")
        else:
            self.logger.error(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """
        Callback when the client disconnects from the broker.

        :param client: The client instance.
        :param userdata: Private user data.
        :param rc: Disconnection result.
        """
        self.logger.info("Disconnected from MQTT Broker")
        if rc != 0:
            self.logger.warning(f"Unexpected disconnection. Return code: {rc}")

    def on_publish(self, client, userdata, mid):
        """
        Callback when a message is published.

        :param client: The client instance.
        :param userdata: Private user data.
        :param mid: Message ID.
        """
        self.logger.debug(f"Message {mid} published.")

    def connect(self):
        """
        Connect to the MQTT broker and start the network loop.
        """
        try:
            self.client.connect(self.server, self.port, self.keepalive)
            self.client.loop_start()
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT Broker: {e}")
            raise

    def disconnect(self):
        """
        Disconnect from the MQTT broker and stop the network loop.
        """
        self.client.loop_stop()
        self.client.disconnect()

    def publish_command(self, command: str):
        """
        Wrap the command in a JSON message and publish to the MQTT topic.

        :param command: The command string to publish.
        """
        message = {"msg": command}
        payload = json.dumps(message)
        try:
            result = self.client.publish(self.topic, payload)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                self.logger.error(f"Failed to publish message: {result}")
            else:
                self.logger.info(f"Published message to {self.topic}: {payload}")
        except Exception as e:
            self.logger.error(f"Exception during publish: {e}")
            raise
