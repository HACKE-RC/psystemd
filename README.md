# psystemd

`psystemd` is a Python library that provides an easy-to-use interface for managing systemd services via DBus. It allows users to check the status of services, start, stop, restart, and enable them, as well as retrieve error details if available.

## Features
- Retrieve the status (ActiveState, SubState) of a systemd service
- Start, stop, restart, and enable services
- Retrieve error-related information (Result, ExecMainStatus, ExecMainCode) if available

## Requirements
- Python 3.x
- `python-dbus` package
- A Linux distribution that uses `systemd`

## Installation
Ensure that `python-dbus` is installed:
```sh
sudo apt install python3-dbus  # Debian-based
sudo dnf install python3-dbus  # Fedora-based
```
Then, clone the repository:
```sh
git clone https://github.com/yourusername/psystemd.git
cd psystemd
```

## Usage

### Example
```python
from psystemd import SystemdServiceManager

service_name = "ssh.service"  # Change this to your desired service
manager = SystemdServiceManager()

# Check the status of the service
status = manager.get_unit_status(service_name)
print(f"Status of {service_name}: {status}")

# Start the service
manager.start(service_name)

# Retrieve errors if any
errors = manager.get_errors(service_name)
print(f"Error information for {service_name}: {errors}")
```

## API Reference

### `get_unit_status(service_name: str) -> dict`
Retrieves the status of the specified service.

**Returns:**
```python
{
    "ActiveState": "active" | "inactive" | "failed" | ...,
    "SubState": "running" | "dead" | "exited" | ...
}
```

### `start(service_name: str)`
Starts the specified service.

### `stop(service_name: str)`
Stops the specified service.

### `restart(service_name: str)`
Restarts the specified service.

### `enable(service_name: str)`
Enables the service to start at boot.

### `get_errors(service_name: str) -> dict`
Retrieves error-related properties, if available.

**Returns:**
```python
{
    "Result": "success" | "failed" | "timeout" | ...,
    "ExecMainStatus": 0 (success) | nonzero (error code),
    "ExecMainCode": 0 (exited cleanly) | other values
}
```
