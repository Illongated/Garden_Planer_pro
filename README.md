# Agrotique Garden Planner

This project is a complete, production-ready plant catalog system for the Agrotique Garden Planner. It features a modern, full-stack architecture with a FastAPI backend and a React frontend, containerized with Docker for easy setup and deployment.

## Features

- **Complete Plant Database**: A comprehensive catalog of vegetables, herbs, and flowers with agronomic metadata.
- **Advanced Search & Filtering**: A full-text search API with filters for plant type, planting season, and sun requirements.
- **Drag & Drop UI**: A React-based palette component allows users to drag plants onto a garden canvas.
- **User Favorites**: Client-side persistence of favorite plants using Zustand and localStorage.
- **Responsive Views**: Switch between grid and list views for the plant catalog.
- **High Performance**: Utilizes React Query for intelligent caching and a debounced search for a smooth user experience.
- **Fully Typed**: Strict TypeScript on the frontend and Pydantic models on the backend for robust, type-safe code.

## Tech Stack

- **Backend**: FastAPI, Pydantic, Uvicorn
- **Frontend**: React, TypeScript, Vite, React Query, Zustand, dnd-kit, Axios
- **Orchestration**: Docker, Docker Compose

## Project Structure

```
.
├── backend/
│   ├── app/                # FastAPI application source
│   ├── data/               # Plant data in JSON format
│   ├── Dockerfile          # Dockerfile for the backend
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── public/             # Public assets
│   ├── src/                # React application source
│   ├── Dockerfile          # Dockerfile for the frontend
│   └── package.json        # Node.js dependencies
├── docker-compose.yml      # Orchestrates the frontend and backend services
└── README.md               # This file
```

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your machine.
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop).

### Running the Application

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Build and run the containers:**
    Open a terminal in the project root and run the following command:
    ```bash
    docker compose up --build
    ```
    This command will:
    - Build the Docker images for both the `backend` and `frontend` services.
    - Start the containers.
    - The `--build` flag ensures that the images are rebuilt if there are any changes to the Dockerfiles or source code.

3.  **Access the application:**
    - The **Frontend Application** will be available at `http://localhost:3000`.
    - The **Backend API** will be available at `http://localhost:8000`. You can access the auto-generated API documentation at `http://localhost:8000/docs`.

### Stopping the Application

To stop the running containers, press `Ctrl + C` in the terminal where `docker compose up` is running.

To stop and remove the containers, you can run:
```bash
docker compose down
```

## How It Works

- The **backend** is a FastAPI server that serves the plant data from a `plants.json` file. It provides several endpoints for searching, filtering, and retrieving plant information.
- The **frontend** is a React single-page application (SPA) built with Vite. It communicates with the backend API to fetch plant data. The frontend is served by an Nginx web server in its Docker container.
- **Docker Compose** orchestrates the two services, creating a network for them to communicate. The Vite development server's proxy is configured to forward requests from `/api` to the backend container, avoiding CORS issues during development and mimicking a production setup.
- **Drag and Drop** is implemented using the `@dnd-kit` library, allowing users to drag plant cards from the palette to the garden canvas.
- **State Management** for UI state like search filters is handled by React's `useState`. Global state, such as user favorites, is managed by `Zustand` for a simple and powerful solution.
- **Data Fetching and Caching** is handled by `@tanstack/react-query`, which provides an excellent developer experience and robust caching, reducing the number of API calls and improving performance.
