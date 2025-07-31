# Garden Planner

This is an intelligent, interactive web application for planning your garden. It helps you create optimized layouts for plants and irrigation systems.

## How to Run

### 1. Prerequisites

- Python 3.7+
- pip

### 2. Installation

1.  **Navigate to your desired directory:**
    ```bash
    cd /path/to/your/projects
    ```
2.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd garden-planner
    ```
    *(Replace `<repository_url>` with the actual URL of the repository)*

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Running the Application

1.  **IMPORTANT:** Make sure you are in the **root directory** of the project (the `garden-planner` directory you just cloned).
2.  **Run the backend server:**
    ```bash
    uvicorn backend.main:app --host 0.0.0.0 --port 8000
    ```
3.  **Open your web browser** and navigate to `http://localhost:8000`. You should see the Garden Planner application.

*(If you see a "Not Found" error, it is almost certainly because you are not running the `uvicorn` command from the root project directory.)*


## How to Use
(Instructions remain the same)

## Technologies Used
(Technologies remain the same)
