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

### Constructor

**`SystemdServiceManager()`**

Connects to the system bus and creates a handle to `org.freedesktop.systemd1.Manager`.

### Query methods

**`get_unit(service_name: str)`**

Returns the raw DBus object for a unit. Tries `GetUnit` first, falling back to `LoadUnit` for units that exist on disk but aren't yet loaded.

Raises `UnitNotFoundError` if the unit cannot be found.

**`get_unit_status(service_name: str) -> dict`**

Returns `{"ActiveState": str, "SubState": str}`.

`ActiveState` is one of `active`, `inactive`, `failed`, `activating`, `deactivating`, `reloading`. `SubState` is the unit-type-specific substate (`running`, `dead`, `exited`, `plugged`, `mounted`, etc.).

**`get_errors(service_name: str) -> dict`**

Returns `{"Result": str, "ExecMainStatus": int, "ExecMainCode": int}` — the result of the last execution. Falls back to `{"Error": "No additional error information available."}` if the unit is not a service type (e.g., a `.mount` or `.socket` unit).

### Control methods

`start`, `stop`, and `restart` enqueue a job with `mode="replace"` and return immediately — the job runs asynchronously. Use `get_unit_status` to confirm the new state.

**`start(service_name: str)`**

Enqueues a start job.

**`stop(service_name: str)`**

Enqueues a stop job.

**`restart(service_name: str)`**

Enqueues a restart job.

**`enable(service_name: str)`**

Symlinks the unit file into the machine's wanted-by targets so it starts at boot. Raises `UnitNotEnabledError` if the unit has no `[Install]` section.
