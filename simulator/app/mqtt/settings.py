"""Configuration model for MQTT telemetry publishing."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MqttSettings:
    """Validated settings used by the MQTT telemetry publisher."""

    host: str = "mqtt"
    port: int = 1883
    client_id: str = "power-grid-simulator"
    qos: int = 1
    keepalive_seconds: int = 60
    connection_timeout_seconds: float = 10.0
    publish_timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        """Validate MQTT settings after object creation."""

        if not self.host.strip():
            raise ValueError("MQTT host cannot be empty.")

        if not 1 <= self.port <= 65535:
            raise ValueError("MQTT port must be between 1 and 65535.")

        if not self.client_id.strip():
            raise ValueError("MQTT client ID cannot be empty.")

        if self.qos not in (0, 1, 2):
            raise ValueError("MQTT QoS must be 0, 1, or 2.")

        if self.keepalive_seconds <= 0:
            raise ValueError("MQTT keepalive must be greater than zero.")

        if self.publish_timeout_seconds <= 0:
            raise ValueError("MQTT publish timeout must be greater than zero.")

        if self.connection_timeout_seconds <= 0:
            raise ValueError("MQTT connection timeout must be greater than zero.")