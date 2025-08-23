import asyncio
import sys
import uvicorn

from src.scheduler import main as run_scheduler
from src.api import app as api_app

async def main():
    """
    Main entry point for the application.
    This script initializes and runs both the scheduler and the API server concurrently.
    """
    # Configure the Uvicorn server to run the FastAPI application
    server_config = uvicorn.Config(
        app=api_app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
    server = uvicorn.Server(server_config)

    print("Starting scheduler and API server...")

    # Use asyncio.gather to run both tasks concurrently
    await asyncio.gather(
        run_scheduler(),
        server.serve()
    )

if __name__ == "__main__":
    """
    This script is the main entry point that launches the entire application.
    """
    print("Application starting...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        # This will catch any unexpected errors during startup or runtime.
        print(f"\nAn unexpected error occurred at the top level: {e}", file=sys.stderr)
        sys.exit(1)

    print("Application finished gracefully.")
