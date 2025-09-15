namespace AlRaseel.Monitor.Core.Models;

public enum DeviceType
{
    PBX,
    Router,
    Switch,
    Server,
    OLT,
    ONT,
    DWDM,
    MicrowaveLink,
    DMR,
    TETRA,
    WiFi,
    LTERouter,
    PC,
    Generator,
    UPS,
    SolarInverter,
    Printer,
    IoTDevice,
    IPCamera,
    VideoDevice,
    ConferencingSystem
}

public enum DeviceStatus
{
    Up,
    Down,
    Warning,
    Unreachable
}

public enum FaultSeverity
{
    Information,
    Warning,
    Critical,
    Emergency
}
