# Power Grid Telemetry Monitor

Power Grid Telemetry Monitor is a containerized event-streaming project that simulates electrical transformer telemetry and gradually processes it through a complete data pipeline.

The project combines software development, data engineering, industrial telemetry, automated testing, and system monitoring. All telemetry is simulated; the project does not connect to or control real electrical equipment.

# Project status

## Completed

- [x] M0: Project preparation, defined architecture, rulles, technologies and goals
- [x] M1: Simulator

## Next steps
- [ ] M2: MQTT broker and telemetry transport
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

## Documentation section

### General docs
- [Project Idea](docs/idea.md)
- [System Architecture](docs/architecture.md)

### Simulator docs
- [Telemetry Simulator](docs/simulator.md)
- [Simulator Usage](simulator/README.md)