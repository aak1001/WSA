# LAN Monitor Backend

This is the backend for the LAN Monitor application. It is a FastAPI application that provides a REST API for discovering and monitoring devices on a local area network.

## Running with Docker

To run the application with Docker, follow these steps:

1.  **Build the Docker image:**

    ```bash
    docker build -t lan-monitor-backend .
    ```

2.  **Run the Docker container:**

    ```bash
    docker run -p 80:80 --net=host lan-monitor-backend
    ```

    *Note: The `--net=host` flag is required for the application to be able to scan the local network.*

## API Endpoints

*   `GET /`: Root endpoint.
*   `GET /discover`: Discover devices on the network.
*   `GET /scan_ports/{ip_address}`: Scan the ports of a device.
*   `GET /snmp_scan/{ip_address}`: Perform an SNMP scan on a device.
*   `GET /check_sip/{ip_address}`: Check the status of a SIP endpoint.
