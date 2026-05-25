# psystemd

A thin Python wrapper around the systemd DBus API for managing services.

## Requirements

- Python 3.x
- `dbus-python` (system package `python3-dbus`)
- A Linux system running systemd
- DBus permissions to manage systemd units (typically requires root or appropriate polkit rules)

## Installation

Install the system dependency, then clone:

```sh
# Debian/Ubuntu
sudo apt install python3-dbus

# Fedora
sudo dnf install python3-dbus

# Arch
sudo pacman -S python-dbus

git clone https://github.com/HACKE-RC/psystemd.git
```

## Usage

```python
from psystemd import SystemdServiceManager

manager = SystemdServiceManager()

# Check status
status = manager.get_unit_status("ssh.service")
print(status)  # {"ActiveState": "active", "SubState": "running"}

# Control the service — returns immediately, job runs asynchronously
manager.stop("ssh.service")
manager.start("ssh.service")
manager.restart("ssh.service")

# Enable at boot (raises UnitNotEnabledError if the unit has no [Install] section)
manager.enable("ssh.service")

# Inspect errors on a failed service
errors = manager.get_errors("my-failed.service")
print(errors)  # {"Result": "exit-code", "ExecMainStatus": 1, "ExecMainCode": 1}
```

## Exceptions

All methods raise `psystemd.SystemdServiceError` (or its subclasses) on failure:

- `SystemdServiceError` — base exception for all psystemd errors
- `UnitNotFoundError` — the unit does not exist on disk or in systemd
- `UnitNotEnabledError` — raised by `enable()` when the unit has no `[Install]` section

## API Reference

### `SystemdServiceManager()`

Connects to the system bus and creates a handle to `org.freedesktop.systemd1.Manager`.

### `get_unit(service_name: str)`

Returns the raw DBus object for a unit. Tries `GetUnit` first, falling back to `LoadUnit` for units that exist on disk but aren't yet loaded. Raises `UnitNotFoundError` if the unit cannot be found.

### `get_unit_status(service_name: str) -> dict`

```python
{"ActiveState": str, "SubState": str}
```

`ActiveState` is one of `active`, `inactive`, `failed`, `activating`, `deactivating`, `reloading`.
`SubState` is the unit-type-specific substate (`running`, `dead`, `exited`, `plugged`, `mounted`, etc.).

### `start(service_name: str)`

Enqueues a start job with `mode="replace"` and returns immediately. The job runs asynchronously — use `get_unit_status` to confirm the new state.

### `stop(service_name: str)`

Enqueues a stop job with `mode="replace"` and returns immediately.

### `restart(service_name: str)`

Enqueues a restart job with `mode="replace"` and returns immediately.

### `enable(service_name: str)`

Symlinks the unit file into the machine's wanted-by targets so it starts at boot. Raises `UnitNotEnabledError` if the unit has no `[Install]` section.

### `get_errors(service_name: str) -> dict`

```python
{"Result": str, "ExecMainStatus": int, "ExecMainCode": int}
```

Returns the result of the last execution. Falls back to `{"Error": "No additional error information available."}` if the unit is not a service type (e.g., a `.mount` or `.socket` unit).
