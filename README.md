# Garden Planner

This is an intelligent, interactive web application for planning your garden. It helps you create optimized layouts for plants and irrigation systems.

## How to Run

### 1. Prerequisites

- Python 3.7+
- pip

### 2. Installation

1.  Clone the repository or download the source code.
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Running the Application

1.  Run the backend server:
    ```bash
    uvicorn backend.main:app --host 0.0.0.0 --port 8000
    ```
2.  Open your web browser and navigate to `http://localhost:8000`.

## How to Use

### Basic Configuration
- **Set Garden Area:** Enter the total area of your garden in square meters.
- **Set Sun Angle:** Enter the angle of the sun at midday (in degrees from North). 180 is South-facing.
- **Set Row Width:** Adjust the slider to set the desired width of the paths between your plants.

### Plant Selection
- Use the **priority sliders** and **lock buttons** to tell the procedural engine which plants are most important to you. The engine will automatically calculate the quantity of each plant that can fit.

### Interactive Editor
The main garden layout is a fully interactive editor:
- **Navigate:** Click and drag the background to rotate the view. Use the scroll wheel to zoom.
- **Select:** Click on any plant, irrigation component, or watering group (the colored boxes) to select it.
- **Move:** Click and drag a selected item to move it to a new location.
- **Undo/Redo:** Use `Ctrl+Z` to undo and `Ctrl+Y` to redo any action.
- **Duplicate:** Hold the `Alt` key and click on a plant to create a copy of it.

### Dashboards
- **Irrigation Dashboard:** Provides a detailed "shopping list" of all the components needed for your irrigation system, broken down by watering zone.
- **Layout Scorecard:** Shows you how well your current layout meets key optimization goals like sun exposure and companion planting.

## Technologies Used

### Backend
- **Python**
- **FastAPI:** A modern, fast web framework for building APIs.
- **Uvicorn:** An ASGI server for running FastAPI.
- **python-socketio:** For real-time, bidirectional communication between the client and server.

### Frontend
- **HTML5, CSS3, JavaScript**
- **Three.js:** A 3D graphics library used to render the interactive garden layout.
- **Zustand:** A small, fast, and scalable state-management solution for the frontend.
