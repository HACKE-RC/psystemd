import psystemd

if __name__ == "__main__":
    service_name = "test.service"  # Change to a valid service name on your system
    manager = psystemd.SystemdServiceManager()

    try:
        # Check status of the service
        status = manager.get_unit_status(service_name)
        print(f"Status of {service_name}: {status}")

        # Uncomment any of the actions below to control the service:
        manager.start(service_name)
        # manager.stop(service_name)
        # manager.restart(service_name)
        # manager.enable(service_name)

        # Retrieve error information if any
        errors = manager.get_errors(service_name)
        print(f"Error information for {service_name}: {errors}")
    except Exception as e:
        print(e)
