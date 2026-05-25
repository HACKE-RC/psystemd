import dbus


class SystemdServiceError(Exception):
    """Base exception for psystemd errors."""
    pass


class UnitNotFoundError(SystemdServiceError):
    """The specified unit was not found."""
    pass


class UnitNotEnabledError(SystemdServiceError):
    """The unit file has no [Install] section and cannot be enabled."""
    pass


class SystemdServiceManager:
    """
    A class to manage systemd services using DBus.

    This library provides methods to:
      - Retrieve the current status of a service.
      - Start, stop, restart, and enable services.
      - Retrieve error information for service units, if available.

    Note:
      Ensure that python-dbus is installed and that the user has the
      necessary privileges to interact with systemd via DBus.
    """

    def __init__(self):
        # Connect to the system bus and get the systemd manager object.
        self.bus = dbus.SystemBus()
        self.systemd_obj = self.bus.get_object('org.freedesktop.systemd1',
                                               '/org/freedesktop/systemd1')
        self.manager = dbus.Interface(self.systemd_obj, 'org.freedesktop.systemd1.Manager')

    def get_unit(self, service_name):
        """
        Retrieve the DBus unit object for a given systemd service.

        Tries GetUnit first, falling back to LoadUnit for units that exist
        on disk but are not yet loaded into systemd's memory.

        :param service_name: Name of the service (e.g., 'ssh.service').
        :return: The DBus object representing the unit.
        :raises UnitNotFoundError: If the service unit cannot be found.
        """
        try:
            unit_path = self.manager.GetUnit(service_name)
        except dbus.DBusException:
            try:
                unit_path = self.manager.LoadUnit(service_name)
            except dbus.DBusException as e:
                raise UnitNotFoundError(f"Unit not found: {service_name}") from e
        return self.bus.get_object('org.freedesktop.systemd1', unit_path)

    def get_unit_status(self, service_name):
        """
        Get the current status of the specified service.

        Retrieves properties such as ActiveState and SubState.

        :param service_name: Name of the service.
        :return: Dictionary with ActiveState and SubState.
        """
        unit = self.get_unit(service_name)
        props = dbus.Interface(unit, 'org.freedesktop.DBus.Properties')
        try:
            active_state = props.Get('org.freedesktop.systemd1.Unit', 'ActiveState')
            sub_state = props.Get('org.freedesktop.systemd1.Unit', 'SubState')
        except dbus.DBusException as e:
            raise SystemdServiceError(f"Error getting status for {service_name}: {e}") from e
        return {"ActiveState": active_state, "SubState": sub_state}

    def start(self, service_name):
        """
        Start the specified service.

        Note: This method returns immediately; the start job runs
        asynchronously. Use get_unit_status to confirm the service
        has reached the desired state.

        :param service_name: Name of the service.
        :raises SystemdServiceError: If an error occurs while starting.
        """
        try:
            self.manager.StartUnit(service_name, "replace")
        except dbus.DBusException as e:
            raise SystemdServiceError(f"Error starting service {service_name}: {e}") from e

    def stop(self, service_name):
        """
        Stop the specified service.

        Note: This method returns immediately; the stop job runs
        asynchronously.

        :param service_name: Name of the service.
        :raises SystemdServiceError: If an error occurs while stopping.
        """
        try:
            self.manager.StopUnit(service_name, "replace")
        except dbus.DBusException as e:
            raise SystemdServiceError(f"Error stopping service {service_name}: {e}") from e

    def restart(self, service_name):
        """
        Restart the specified service.

        Note: This method returns immediately; the restart job runs
        asynchronously.

        :param service_name: Name of the service.
        :raises SystemdServiceError: If an error occurs while restarting.
        """
        try:
            self.manager.RestartUnit(service_name, "replace")
        except dbus.DBusException as e:
            raise SystemdServiceError(f"Error restarting service {service_name}: {e}") from e

    def enable(self, service_name):
        """
        Enable the specified service to start at boot.

        :param service_name: Name of the service file (e.g., 'ssh.service').
        :raises SystemdServiceError: If a DBus error occurs.
        :raises UnitNotEnabledError: If the unit has no [Install] section.
        """
        try:
            carries_install_info, _changes = self.manager.EnableUnitFiles(
                [service_name], False, False)
        except dbus.DBusException as e:
            raise SystemdServiceError(f"Error enabling service {service_name}: {e}") from e
        if not carries_install_info:
            raise UnitNotEnabledError(
                f"Unit {service_name} has no [Install] section and cannot be enabled")

    def get_errors(self, service_name):
        """
        Retrieve error-related properties from the service unit, if available.

        This method tries to query the service-specific interface to obtain
        error-related details, such as the overall "Result" of the last run,
        the "ExecMainStatus", and "ExecMainCode". If these properties are not
        available, it returns a default message.

        :param service_name: Name of the service.
        :return: Dictionary containing error information.
        """
        unit = self.get_unit(service_name)
        props = dbus.Interface(unit, 'org.freedesktop.DBus.Properties')

        try:
            result = props.Get('org.freedesktop.systemd1.Service', 'Result')
            exec_status = props.Get('org.freedesktop.systemd1.Service', 'ExecMainStatus')
            exec_code = props.Get('org.freedesktop.systemd1.Service', 'ExecMainCode')
            return {
                "Result": result,
                "ExecMainStatus": exec_status,
                "ExecMainCode": exec_code
            }
        except dbus.DBusException:
            return {"Error": "No additional error information available."}
