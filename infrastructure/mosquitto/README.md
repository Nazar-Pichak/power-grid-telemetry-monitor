# Eclipse Mosquitto Broker

## Overview

Eclipse Mosquitto provides the MQTT broker used by Milestone 2. It receives telemetry published by the simulator and forwards each message to clients subscribed to the matching topic.

The broker runs from the official `eclipse-mosquitto:2` Docker image. It does not contain custom application code.

## Configuration

The broker configuration is stored in:

```text
infrastructure/mosquitto/mosquitto.conf
```

The local development configuration uses:

| Setting | Value | Purpose |
|---|---:|---|
| Listener address | `0.0.0.0` | Accept connections on all container interfaces |
| Listener port | `1883` | Accept standard MQTT connections |
| Anonymous access | `true` | Allow local development without credentials |
| Persistence | `false` | Keep the broker focused on live transport |
| Log destination | `stdout` | Make logs available through Docker Compose |
| Connection logging | `true` | Record client connections and disconnections |

Anonymous access is suitable only for local development. Production deployment must add authentication, authorization, and TLS encryption.

## Docker Compose

Docker Compose exposes port `1883` on the host for local diagnostic tools. Application containers communicate through the internal Compose network and resolve the broker by its service name `mqtt`.

The broker health check publishes a QoS 1 message. Docker marks the service as healthy only when that operation succeeds.

The simulator depends on the broker through the `service_healthy` condition and starts only after Mosquitto is ready.

## Starting the Broker

Start only the MQTT broker:

```powershell
docker compose up -d mqtt
```

Start the complete Milestone 2 environment:

```powershell
docker compose up --build -d
```

## Broker Status and Logs

Display the broker status:

```powershell
docker compose ps mqtt
```

Display broker logs:

```powershell
docker compose logs mqtt
```

The broker must report a running container with a healthy status.

## Manual Publish and Subscribe Check

Subscribe to all transformer telemetry:

```powershell
docker compose exec mqtt mosquitto_sub `
  -h localhost `
  -p 1883 `
  -t "grid/stations/+/devices/+/telemetry" `
  -q 1 `
  -v
```

In another terminal, publish one simulator cycle through MQTT:

```powershell
docker compose run --rm simulator python -m app.main `
  --cycles 1 `
  --interval 0 `
  --seed 42 `
  --transport mqtt
```

The subscriber must receive one message from each of the 12 transformers.

Run the complete automated test suite:

```powershell
docker compose run --rm simulator-tests pytest `
  --cov=app `
  --cov-report=term-missing
```

Validate the Compose configuration:

```powershell
docker compose config --quiet
```

A valid configuration produces no output and returns exit code `0`.

## Stopping the Broker

Stop only the MQTT broker:

```powershell
docker compose stop mqtt
```

Stop and remove the complete local environment:

```powershell
docker compose down
```
