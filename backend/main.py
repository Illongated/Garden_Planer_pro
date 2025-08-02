import os
import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .api.api_v1.api import api_router

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Intelligent Garden Planner API",
    openapi_url="/api/v1/openapi.json"
)

# --- CORS Middleware ---
# In a production environment, you should restrict this to your frontend's domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# --- API Router ---
app.include_router(api_router, prefix="/api/v1")

# --- Socket.IO Setup ---
# The basic server is kept for potential future real-time features,
# but the complex event handlers have been replaced by the REST API.
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)
app.mount('/socket.io', socket_app)

@sio.event
async def connect(sid, environ):
    # You could add authentication here, e.g., by checking the token in environ
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

# --- Static Files Mount ---
# This should be last, as it's a catch-all route.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
