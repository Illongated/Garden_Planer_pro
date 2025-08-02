# Agrotique Garden Planner API

A modern, production-ready RESTful API for the Agrotique Garden Planner application. Built with FastAPI.

This backend service provides a complete solution for managing garden projects, searching a plant catalogue, and planning optimized layouts and irrigation systems. It features JWT authentication, real-time project synchronization via WebSockets, and Redis caching for high performance.

## ✨ Features

- **🔐 JWT Authentication**: Secure endpoints with access and refresh tokens (`/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/me`).
- **📝 Project Management**: Full CRUD operations for user-owned garden projects (`/projects`).
- **WebSocket Real-time Sync**: Live project updates are broadcast to connected clients (`/ws/{project_id}`).
- **🌱 Plant Catalogue**: A comprehensive, searchable, and filterable catalogue of plants (`/plants`).
- **🧠 Layout Optimizer**: An endpoint to calculate an optimized garden layout based on plant positions and constraints (`/layout/optimize`). (Mock Implementation)
- **💧 Irrigation Planner**: Endpoints to compute watering zones and flow/pressure requirements (`/irrigation`). (Mock Implementation)
- **📤 Export System**: Export project plans to JSON, PDF, or PNG formats (`/export`). (PDF/PNG are Mock Implementations)
- **⚡ High Performance**: Redis caching for plant catalogue and export results.
- **🛡️ Secure & Robust**: Rate limiting, central error handling, and strict data validation with Pydantic.
- **📚 OpenAPI Documentation**: Interactive API documentation (Swagger UI) available at `/docs`.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Redis server (running on `localhost:6379` by default)

### 1. Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 2. Running the Application

1.  **Start the FastAPI server:**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The `--reload` flag enables hot-reloading, which is useful for development.

2.  **Access the API:**
    The API will be available at `http://localhost:8000`.

3.  **View the Interactive Documentation:**
    Open your browser and navigate to `http://localhost:8000/docs`. You will see the Swagger UI, which allows you to interact with all the API endpoints.

### 3. Running the Tests

To ensure everything is working correctly, you can run the test suite using `pytest`.

1.  **From the root of the project, run:**
    ```bash
    pytest
    ```

## 🏗️ Project Structure

The project follows a modern, scalable structure:

```
app/
├── api/              # API specific code
│   └── v1/
│       ├── endpoints/  # Individual endpoint files (auth.py, projects.py, etc.)
│       └── api.py      # Main API router aggregating all endpoints
├── core/             # Core components (config, security)
├── db/               # Mock database data
├── schemas/          # Pydantic schemas for data validation
├── services/         # Business logic (optimizers, planners, websocket manager)
├── tests/            # Pytest tests
├── utils.py          # Utility functions
└── main.py           # Main FastAPI application instance
```
