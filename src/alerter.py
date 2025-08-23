import yaml
from typing import Dict, Any, List

# A simple in-memory store to track the state of alerts.
# This helps prevent sending the same alert repeatedly.
# Key: alert rule name + device host, Value: True (alert is active)
# e.g., {"device_unreachable_10.10.10.5": True}
_ACTIVE_ALERTS = {}

def _load_alert_rules() -> List[Dict[str, Any]]:
    """Loads alert rules from the configuration file."""
    try:
        with open("configs/config.yaml", 'r') as f:
            config = yaml.safe_load(f)
            return config.get("alerts", {}).get("rules", [])
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Error loading alert rules: {e}")
        return []

def _evaluate_condition(condition: str, status: Dict[str, Any]) -> bool:
    """
    A very simple and safe evaluator for alert conditions.
    It does NOT use eval(). It only supports basic checks.

    Examples of supported conditions:
    - "status.snmp_error is not None"
    - "status.is_reachable == False" (assuming is_reachable is in status)
    """
    parts = condition.split()
    if len(parts) != 4 or parts[0].split('.')[0] != 'status':
        return False # Unsupported condition format

    # e.g., status.snmp_error
    key = parts[0].split('.')[1]
    # e.g., is
    operator = parts[1]
    # e.g., not
    negation = parts[2]
    # e.g., None
    value = parts[3]

    # Check for 'is not None'
    if operator == 'is' and negation == 'not' and value == 'None':
        return key in status and status[key] is not None

    # Add more simple checks here in the future
    # For now, this is all we need for the "unreachable" alert.

    return False

def _execute_actions(rule: Dict, device_host: str, status: Dict):
    """Executes the actions defined in a rule."""
    for action in rule.get("actions", []):
        if action.get("type") == "log":
            message = action.get("message", "No message configured.")
            # Simple templating
            message = message.replace("{{ name }}", rule.get("name", "N/A"))
            message = message.replace("{{ host }}", device_host)
            # Replace status fields, e.g., {{ status.snmp_error }}
            for key, val in status.items():
                message = message.replace(f"{{{{ status.{key} }}}}", str(val))

            print(f"\n--- ALERT ---")
            print(message)
            print(f"-------------\n")

def check_alerts_for_device(device_host: str, status: Dict[str, Any]):
    """
    Checks all alert rules against the latest status of a single device.
    """
    rules = _load_alert_rules()
    if not rules:
        return

    for rule in rules:
        alert_key = f"{rule['name']}_{device_host}"

        try:
            condition_met = _evaluate_condition(rule["condition"], status)
        except Exception as e:
            print(f"Error evaluating condition for rule '{rule['name']}': {e}")
            continue

        is_alert_active = _ACTIVE_ALERTS.get(alert_key, False)

        if condition_met and not is_alert_active:
            # New alert! Trigger actions and mark as active.
            print(f"New alert triggered for rule '{rule['name']}' on device {device_host}")
            _execute_actions(rule, device_host, status)
            _ACTIVE_ALERTS[alert_key] = True
        elif not condition_met and is_alert_active:
            # Alert has cleared. Mark as inactive.
            print(f"Alert '{rule['name']}' has cleared for device {device_host}")
            del _ACTIVE_ALERTS[alert_key]
        # Otherwise, no change in state, so do nothing.
