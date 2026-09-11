# Power Grid Telemetry Monitor

Power Grid Telemetry Monitor is a containerized event-streaming project that simulates electrical transformer telemetry and gradually processes it through a complete data pipeline.

The project combines software development, data engineering, industrial telemetry, automated testing, and system monitoring. All telemetry is simulated; the project does not connect to or control real electrical equipment.

## Requirements

- Docker
- Docker Compose plugin

All commands must be executed from the project root.

## Quick Start

Start the MQTT broker and the continuously running MQTT simulator:

```powershell
docker compose up --build -d
docker compose logs -f simulator
```

Stop and remove the local environment:

```powershell
docker compose down
```

The simulator CLI defaults to console output when invoked directly. The
`simulator` Compose service explicitly selects MQTT transport.

Run the complete automated test suite:

```powershell
docker compose run --rm simulator-tests
```

Validate the Compose configuration:

```powershell
docker compose config --quiet
```

# Project status

## Completed

- [x] M0: Project preparation, defined architecture, rules, technologies and goals
- [x] M1: Simulator
- [x] M2: MQTT broker and telemetry transport

## Next steps
- [ ] M3: MQTT-Kafka Bridge
- [ ] M4: Redpanda and dead-letter topic
- [ ] M5: Stream Processor
- [ ] M6: PostgreSQL schema and migration runner
- [ ] M7: FastAPI
- [ ] M8: React Dashboard
- [ ] M9: Monitoring Worker
- [ ] M10: Integration, end-to-end, and resilience testing
- [ ] M11: Retention and storage management
- [ ] M12: Production deployment

No later milestone may be marked complete before all checks for its predecessor
have passed.

# Documentation section

## General docs

- [Project Idea](docs/idea.md)
- [System Architecture](docs/architecture.md)

## Simulator docs

- [Telemetry Simulator](docs/simulator.md)
- [Simulator Usage](simulator/README.md)

## MQTT docs

- [MQTT Broker and Telemetry Transport](docs/mqtt.md)
- [Mosquitto Broker Usage](infrastructure/mosquitto/README.md)
