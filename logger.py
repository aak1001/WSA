import datetime

def log_event(event):
    with open("lan_monitor.log", "a") as f:
        f.write(f"{datetime.datetime.now()} - {event}\n")
