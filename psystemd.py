import dbus


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

        :param service_name: Name of the service (e.g., 'ssh.service').
        :return: The DBus object representing the unit.
        :raises Exception: If the service unit cannot be found.
        """
        try:
            unit_path = self.manager.GetUnit(service_name)
            return self.bus.get_object('org.freedesktop.systemd1', unit_path)
        except dbus.DBusException as e:
            raise Exception(f"Error retrieving unit for {service_name}: {e}")

    def get_unit_status(self, service_name):
        """
        Get the current status of the specified service.

        Retrieves properties such as ActiveState and SubState.

        :param service_name: Name of the service.
        :return: Dictionary with ActiveState and SubState.
        """
        unit = self.get_unit(service_name)
        props = dbus.Interface(unit, 'org.freedesktop.DBus.Properties')
        active_state = props.Get('org.freedesktop.systemd1.Unit', 'ActiveState')
        sub_state = props.Get('org.freedesktop.systemd1.Unit', 'SubState')
        return {"ActiveState": active_state, "SubState": sub_state}

    def start(self, service_name):
        """
        Start the specified service.

        :param service_name: Name of the service.
        :raises Exception: If an error occurs while starting the service.
        """
        try:
            self.manager.StartUnit(service_name, "replace")
        except dbus.DBusException as e:
            raise Exception(f"Error starting service {service_name}: {e}")

    def stop(self, service_name):
        """
        Stop the specified service.

        :param service_name: Name of the service.
        :raises Exception: If an error occurs while stopping the service.
        """
        try:
            self.manager.StopUnit(service_name, "replace")
        except dbus.DBusException as e:
            raise Exception(f"Error stopping service {service_name}: {e}")

    def restart(self, service_name):
        """
        Restart the specified service.

        :param service_name: Name of the service.
        :raises Exception: If an error occurs while restarting the service.
        """
        try:
            self.manager.RestartUnit(service_name, "replace")
        except dbus.DBusException as e:
            raise Exception(f"Error restarting service {service_name}: {e}")

    def enable(self, service_name):
        """
        Enable the specified service to start at boot.

        Note: systemd expects a list of unit file names.

        :param service_name: Name of the service.
        :raises Exception: If an error occurs while enabling the service.
        """
        try:
            # The EnableUnitFiles method expects a list of unit file names.
            self.manager.EnableUnitFiles([service_name], False, True)
        except dbus.DBusException as e:
            raise Exception(f"Error enabling service {service_name}: {e}")

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

        # Attempt to get properties specific to service units.
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
            # If these properties aren't available, provide a fallback message.
            return {"Error": "No additional error information available."}
