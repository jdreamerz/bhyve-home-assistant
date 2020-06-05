# bhyve-home-assistant

Orbit BHyve component for [Home Assistant](https://www.home-assistant.io/).

If this integration has been useful to you, please consider chipping in and buying me a coffee!

<a href="https://www.buymeacoffee.com/sebr" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee"></a>

## Supported Entities

- `sensor` for measuring battery levels of `sprinkler_timer` devices as well as the device on/off state (not to be confused with zone on/off switches)
- `binary_sensor` for tracking rain/weather delays
- `switch` for turning a zone on/off

## Installation

Recommended installation is via HACS.

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

## Configuration

```yaml
bhyve:
  username: !secret bhyve_username
  password: !secret bhyve_password

sensor:
  - platform: bhyve

switch:
  - platform: bhyve
```

## Sensor Entities

### Battery Sensor

A **battery** `sensor` entity is created for any device which has a battery level to report.

### Zone State sensor

A **zone state** `sensor` entity is created for each zone. This reports the state of the zone, for example `auto` or `off`. A zone may be switched to `off` either manually through the BHyve app, or may be automatically set when battery levels are too low to operate the device correctly.

## Switch Entities

### Zone Switch

A **zone** `switch` entity is created for each zone of a `sprinkler_timer` device. This switch enables starting/stopping irrigation of a zone. Turning on the switch will enable watering of the zone for the amount of time configured in the BHyve app.

The following attributes are set on zone switch entities:

| Attribute                     | Type           | Notes                                                                                             |
| ----------------------------- | -------------- | ------------------------------------------------------------------------------------------------- |
| `manual_preset_runtime`       | `number`       | The number of seconds to run zone watering when switch is turned on.                              |
| `smart_watering_enabled`      | `boolean`      | True if the zone has a smart water schedule enabled.                                              |
| `sprinkler_type`              | `string`       | The configured type of sprinker.                                                                  |
| `image_url`                   | `string`       | The url to zone image.                                                                            |
| `started_watering_station_at` | `string`       | The timestamp the zone started watering.                                                          |
| `watering_program`            | `list[string]` | List of timestamps for future/scheduled watering times.<sup>†</sup>                               |
| `program_x`                   | `Object`       | Provides details on any configured watering programs for the given switch. See below for details. |

<sup>†</sup> Only applicable if a Smart Watering program is enabled. Any rain delays or other custom programs must be considered separately.

#### `program_x` attribute

Any watering programs which are configured for a zone switch are made available as an attribute. The `X` denotes the letter of the program slot. Values `A`, `B` and `C` are well known custom slots. Program `E` is reserved for the Smart Watering plan. Slot `D` does not have a known use at this stage.

```json
{
  "enabled": true,
  "name": "Backyard",
  "is_smart_program": false,
  "start_times": ["07:30"],
  "frequency": {
    "type": "days",
    "days": [1, 4]
  },
  "run_times": [
    {
      "run_time": 20,
      "station": 1
    }
  ]
}
```

- `start_times`, `frequency` and `run_time` are not present on `program_e` (Smart Watering program)
- `frequency` days: `0` is Sunday, `1` is Monday etc...
- `run_time` is in minutes

### Rain Delay Switch

A **rain delay** `switch` entity is created for each discovered `sprinkler_timer` device. This entity will be **on** whenever BHyve reports that a device's watering schedule will be delayed due to weather conditions.

The following attributes are set on `binary_sensor.*_rain_delay` entities, if the sensor is on:

| Attribute      | Type     | Notes                                                                                     |
| -------------- | -------- | ----------------------------------------------------------------------------------------- |
| `cause`        | `string` | Why a delay was put in place. Values seen: `auto`. May be empty.                          |
| `delay`        | `number` | The number of hours the delay is in place. NB: This is hours from `started_at` attribute. |
| `weather_type` | `string` | The reported cause of the weather delay. Values seen: `wind`, `rain`. May be empty.       |
| `started_at`   | `string` | The timestamp the delay was put in place.                                                 |

## Python Script

Bundled in this repository is a [`python_script`](https://www.home-assistant.io/integrations/python_script) which calculates a device's next watering time and when a rain delay is scheduled to finish.

Note: HACS does not install the script automatically and they must be added manually to your HA instance.

### Scripts

#### [`bhyve_next_watering.py`](https://github.com/sebr/bhyve-home-assistant/blob/master/python_scripts/bhyve_next_watering.py)

Calculates:

1. When the next scheduled watering is for a device by considering all enabled watering programs
2. When an active rain delay will finish, or `None` if there is no active delay

This script creates or updates entities named `sensor.next_watering_{device_name}` and `sensor.rain_delay_finishing_{device_name}`.

Usage:

```yaml
service: python_script.bhyve_next_watering
data:
  entity_id: switch.backyard_zone
```

Required argument is the switch entity_id for the device.

### Automation

Hook these scripts up to automations to update as required:

```yaml
automation:
  - alias: BHyve next watering & rain delay finishing updater
    trigger:
      - platform: state
        entity_id: switch.backyard_zone, switch.rain_delay_lawn
      - platform: homeassistant
        event: start
    action:
      - service: python_script.bhyve_next_watering
        data:
          entity_id: switch.backyard_zone
```

## Debugging

To debug this integration and provide device integration for future improvements, please enable debugging in Home Assistant's `configuration.yaml`

```yaml
logger:
  logs:
    custom_components.bhyve: debug
    pybhyve: debug

bhyve:
  username: !secret bhyve_username
  password: !secret bhyve_password
  packet_dump: true # Save all websocket event data to a file
  conf_dir: "" # Storage directory for packet dump file. Usually not needed, defaults to hass_config_dir/.bhyve
```
