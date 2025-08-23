from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from . import database

# Create the FastAPI application instance
app = FastAPI(
    title="Network Monitoring API",
    description="API for the portable network monitoring tool.",
    version="0.1.0",
)

# --- Pydantic Models for API data structure ---

class DeviceStatus(BaseModel):
    """Pydantic model for representing the status of a single device."""
    host: str
    last_seen: str = Field(..., description="The timestamp in ISO format when the device was last seen.")
    is_reachable: bool = Field(..., description="Whether the device was reachable on the last poll.")
    metrics: Dict[str, Any] # Using Dict directly is often simpler if no validation is needed

# --- API Endpoints ---

@app.get("/api/status", tags=["Health"])
async def get_status():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "ok"}

@app.get("/api/devices", response_model=List[DeviceStatus], tags=["Devices"])
async def get_devices():
    """
    Retrieves the latest status for all monitored devices.
    The data is fetched from the SQLite database.
    """
    try:
        device_statuses = database.get_all_device_statuses()
        return device_statuses
    except Exception as e:
        # In a real app, you'd have more specific error handling and logging
        return {"error": "Could not retrieve device statuses", "details": str(e)}

# --- Static File Serving ---
# Mount the directories containing CSS and JS files
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")

@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def read_root():
    """Serves the main index.html file."""
    with open("frontend/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# To run this API directly for testing:
# uvicorn src.api:app --reload
# The main application will run it programmatically via run.py.
