import json

KNOWN_DEVICES_FILE = "known_devices.json"

def get_known_devices():
    try:
        with open(KNOWN_DEVICES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_known_devices(devices):
    with open(KNOWN_DEVICES_FILE, "w") as f:
        json.dump(devices, f, indent=4)

def check_for_new_devices(discovered_devices):
    known_devices = get_known_devices()
    known_macs = [device["mac"] for device in known_devices]
    new_devices = []

    for device in discovered_devices:
        if device["mac"] not in known_macs:
            new_devices.append(device)
            known_devices.append(device)

    if new_devices:
        save_known_devices(known_devices)

    return new_devices
