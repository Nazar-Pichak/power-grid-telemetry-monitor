"""Tests for the console telemetry publisher."""

from io import StringIO
from unittest.mock import Mock

from app.console_publisher import ConsoleTelemetryPublisher
from app.publisher import TelemetryPublisher
from app.telemetry import TelemetryMessage


def test_console_publisher_implements_publisher_protocol() -> None:
    """Console publisher satisfies the telemetry publisher protocol."""

    publisher = ConsoleTelemetryPublisher(output=StringIO())

    assert isinstance(publisher, TelemetryPublisher)


def test_publish_writes_serialized_message_with_newline() -> None:
    """Publisher writes one JSON message followed by a newline."""

    output = StringIO()
    message = Mock(spec=TelemetryMessage)
    message.model_dump_json.return_value = '{"deviceCode":"TRF-PLN-01"}'

    publisher = ConsoleTelemetryPublisher(output=output)

    publisher.connect()
    publisher.publish(message)
    publisher.close()

    assert output.getvalue() == '{"deviceCode":"TRF-PLN-01"}\n'
    message.model_dump_json.assert_called_once_with(by_alias=True)