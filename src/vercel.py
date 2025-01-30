import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Load environment variables
load_dotenv()

# Import the main FastAPI app
from main import app as main_app

# Create the Vercel app instance
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the absolute path to the project root
ROOT_DIR = Path(__file__).parent.parent
STATIC_DIR = ROOT_DIR / "src" / "ui" / "dist" / "assets"
HTML_FILE = ROOT_DIR / "src" / "ui" / "dist" / "index.html"

# Include the routes from main app
for route in main_app.routes:
    app.routes.append(route)

# Serve static files if they exist
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR)), name="static")
    print("Serving React app")

    @app.get("/")
    async def serve_root():
        if HTML_FILE.exists():
            return FileResponse(str(HTML_FILE))
        raise HTTPException(status_code=404, detail="Frontend not built")

    @app.get("/{catchall:path}")
    async def serve_react_app(catchall: str):
        if HTML_FILE.exists():
            return FileResponse(str(HTML_FILE))
        raise HTTPException(status_code=404, detail="Frontend not built")

if __name__ == "__main__":
    import uvicorn
    
    # Parse command line arguments for server configuration
    default_host = os.getenv("HOST", "0.0.0.0")
    default_port = int(os.getenv("FAST_API_PORT", "7860"))

    parser = argparse.ArgumentParser(description="FastAPI server for Vercel")
    parser.add_argument("--host", type=str, default=default_host, help="Host address")
    parser.add_argument("--port", type=int, default=default_port, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Reload code on change")

    args = parser.parse_args()

    # Start the FastAPI server
    uvicorn.run(
        "vercel:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
