import ipaddress
import subprocess
import platform
import asyncio
import csv
from typing import List, Dict

async def _ping_host(ip: ipaddress.IPv4Address) -> bool:
    """
    Pings a single host and returns True if reachable, False otherwise.
    Uses asyncio for concurrent execution.
    """
    # Use -n 1 for Windows, -c 1 for others. Timeout of 1 second (-w 1).
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-w', '1', str(ip)]

    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    await proc.wait()
    return proc.returncode == 0

async def ping_sweep(subnet: str) -> List[str]:
    """
    Performs an asynchronous ICMP ping sweep on a given subnet.
    Returns a list of reachable IP addresses.
    e.g., await ping_sweep('192.168.1.0/24')
    """
    reachable_hosts = []
    try:
        network = ipaddress.ip_network(subnet, strict=False)
    except ValueError:
        print(f"Error: Invalid subnet '{subnet}'")
        return reachable_hosts

    tasks = []
    host_list = list(network.hosts())

    for ip in host_list:
        tasks.append(asyncio.create_task(_ping_host(ip)))

    results = await asyncio.gather(*tasks)

    for i, is_reachable in enumerate(results):
        if is_reachable:
            reachable_hosts.append(str(host_list[i]))

    return reachable_hosts

def import_from_csv(filepath: str) -> List[Dict]:
    """
    Imports device information from a CSV file.
    Assumes the CSV has a header row (e.g., ip_address,hostname,type).
    Returns a list of dictionaries, where each dictionary represents a device.
    """
    devices = []
    try:
        # Use utf-8-sig to handle potential BOM at the start of the file
        with open(filepath, mode='r', encoding='utf-8-sig', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                devices.append(row)
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'")
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
    return devices

if __name__ == '__main__':
    # Example usage (for testing purposes)

    # 1. Test CSV import
    print("Testing CSV import...")
    # Create a dummy CSV for testing
    dummy_csv_path = 'data/devices.csv'
    with open(dummy_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ip_address', 'hostname', 'type'])
        writer.writerow(['10.10.10.5', 'alcatel-oxe-1', 'alcatel_oxe'])
        writer.writerow(['10.10.20.8', 'nortel-cs1000', 'nortel_cs1000'])

    imported_devices = import_from_csv(dummy_csv_path)
    if imported_devices:
        print(f"Successfully imported {len(imported_devices)} devices:")
        for device in imported_devices:
            print(f"  - {device}")
    else:
        print("CSV import failed or file was empty.")

    # 2. Test Ping Sweep (will be very limited in a sandboxed environment)
    print("\nTesting ping sweep...")
    # This will likely not find any hosts in a typical container environment,
    # but it tests the function's logic.
    async def test_ping():
        # Using a small, private subnet for the test
        local_subnet = '192.168.1.0/30'
        print(f"Sweeping subnet {local_subnet}. This might take a moment...")
        found_hosts = await ping_sweep(local_subnet)
        if found_hosts:
            print(f"Found reachable hosts: {found_hosts}")
        else:
            print("No reachable hosts found (as expected in this environment).")

    # The sandbox might not have a running event loop, so we run our own.
    try:
        asyncio.run(test_ping())
    except Exception as e:
        print(f"Asyncio test failed: {e}")
