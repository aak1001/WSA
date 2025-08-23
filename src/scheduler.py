import yaml
import asyncio
from typing import Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from . import database
from . import alerter
# Import collector classes
from .collectors.snmp import SnmpCollector
# As we add more collectors (e.g., SSH), we will import them here.

# A mapping from collector names in the config file to the actual Python classes.
COLLECTOR_MAP = {
    "snmp": SnmpCollector,
    # "ssh": SshCollector, # Example for the future
}

def load_config(path: str = "configs/config.yaml") -> Dict[str, Any]:
    """Loads the YAML configuration file."""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at '{path}'")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return {}

async def run_collection_job(collector_instance: Any):
    """
    A wrapper function for the scheduler to call.
    It executes the collector's main method and handles the output.

    Note: The current SnmpCollector.collect() is a blocking I/O call.
    For better performance with many devices, it should be run in a thread pool
    or converted to be fully async. For now, this is sufficient.
    """
    device_host = collector_instance.device.get('host', 'N/A')
    collector_name = collector_instance.__class__.__name__

    print(f"[{asyncio.get_running_loop().time():.2f}] Running {collector_name} for {device_host}...")

    # In a real-world async app, we'd run blocking calls in an executor
    # loop = asyncio.get_running_loop()
    # data = await loop.run_in_executor(None, collector_instance.collect)
    data = collector_instance.collect() # Keep it simple for now

    # Save the collected data to the database
    try:
        database.update_device_status(host=device_host, data=data)
        print(f"  -> Successfully saved data for {device_host}: {data}")
        # After saving, check for alerts on the new data
        alerter.check_alerts_for_device(device_host, data)
    except Exception as e:
        print(f"  -> Error saving data or checking alerts for {device_host}: {e}")

async def main():
    """The main entry point for the scheduler application."""
    print("Initializing scheduler...")
    config = load_config()
    if not config:
        print("Could not load configuration. Exiting.")
        return

    devices = config.get("devices", [])
    profiles = config.get("profiles", {})
    poll_interval = config.get("instance", {}).get("poll_interval", 300) # Default to 5 mins

    scheduler = AsyncIOScheduler(timezone=config.get("instance", {}).get("timezone", "UTC"))

    for device in devices:
        device_type = device.get("type")
        if not device_type or device_type not in profiles:
            print(f"Warning: No valid profile found for device {device.get('host')}. Skipping.")
            continue

        profile_collectors = profiles[device_type]
        for collector_profile in profile_collectors:
            collector_name = collector_profile.get("collector")
            CollectorClass = COLLECTOR_MAP.get(collector_name)

            if CollectorClass:
                instance = CollectorClass(device, collector_profile)
                # Use the profile's 'name' for a more specific job ID, fallback to collector type
                profile_name = collector_profile.get("name", collector_name)
                job_id = f"{device['host']}_{profile_name}"
                print(f"Scheduling job '{job_id}' to run every {poll_interval} seconds.")
                scheduler.add_job(
                    run_collection_job,
                    'interval',
                    seconds=int(poll_interval),
                    args=[instance],
                    id=job_id
                )
            else:
                print(f"Warning: Collector type '{collector_name}' is not recognized. Skipping.")

    if scheduler.get_jobs():
        scheduler.start()
        print("Scheduler started successfully. Press Ctrl+C to exit.")
        try:
            # Keep the application running indefinitely.
            while True:
                await asyncio.sleep(3600)
        except (KeyboardInterrupt, SystemExit):
            print("Scheduler shutting down...")
            scheduler.shutdown()
            print("Scheduler stopped.")
    else:
        print("No jobs were scheduled. Please check your configuration. Exiting.")

if __name__ == "__main__":
    # To run this script: python -m src.scheduler
    # The `-m` is important if running from the root directory
    # so that imports like `from collectors.snmp` work correctly.
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
