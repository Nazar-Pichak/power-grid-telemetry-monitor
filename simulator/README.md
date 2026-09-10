# Power Grid Telemetry Simulator

Containerized Python simulator that generates validated transformer telemetry as JSON Lines.

Detailed design documentation is available in [Telemetry Simulator](../docs/simulator.md).

## Requirements

- Docker
- Docker Compose

All commands below must be executed from the project root.

## Build

Build the runtime image:

```powershell
docker compose build simulator
```

Build the test image:

```powershell
docker compose build simulator-tests
```

## Finite Simulation

Run one cycle without delay:

```powershell
docker compose run --rm simulator python -m app.main `
    --cycles 1 `
    --interval 0 `
    --seed 42
```

One cycle produces twelve JSON messages.

Run two deterministic cycles:

```powershell
docker compose run --rm simulator python -m app.main `
    --cycles 2 `
    --interval 0 `
    --seed 42
```

## Continuous Simulation

Run continuously with a one-second interval:

```powershell
docker compose run --rm simulator python -m app.main `
    --interval 1 `
    --seed 42
```

Stop the simulator with `Ctrl+C`.

## Fault Scenario

Apply overheating to one selected transformer:

```powershell
docker compose run --rm simulator python -m app.main `
    --cycles 2 `
    --interval 0 `
    --seed 42 `
    --device-code TRF-PLN-02 `
    --scenario overheating
```

Supported scenarios:

- `normal`
- `overvoltage`
- `undervoltage`
- `overload`
- `overheating`
- `frequency_high`

## CLI Options

Display all available options:

```powershell
docker compose run --rm simulator python -m app.main --help
```

| Argument | Description |
|---|---|
| `--cycles` | Number of cycles; omitted for continuous execution |
| `--interval` | Delay between cycles in seconds |
| `--seed` | Optional deterministic random seed |
| `--device-code` | Transformer selected for a fault scenario |
| `--scenario` | Scenario applied to the selected transformer |

## Tests

Run the complete test suite with coverage:

```powershell
docker compose run --rm simulator-tests
```

Run one test module:

```powershell
docker compose run --rm simulator-tests pytest -v tests/test_fleet.py
```

Final Milestone 1 test result:

```text
166 passed
99% statement coverage
```

## Output

The simulator writes one compact JSON object per line.

Example:

```json
{
  "schemaVersion": "1.0",
  "messageId": "f1f17713-cc5b-477c-99c2-c6e190837e60",
  "timestamp": "2026-09-09T00:42:38.902784Z",
  "stationCode": "PLZEN-NORTH",
  "deviceCode": "TRF-PLN-01",
  "sequence": 1,
  "voltageV": 400.675,
  "currentA": 236.834,
  "frequencyHz": 50.002,
  "powerFactor": 0.9332,
  "activePowerKw": 153.381,
  "temperatureC": 43.015,
  "status": "normal",
  "simulated": true
}
```

Each line represents one complete and independently validated transformer telemetry message.

## Related Documentation

- [Project Idea](../docs/idea.md)
- [System Architecture](../docs/architecture.md)
- [Telemetry Simulator](../docs/simulator.md)