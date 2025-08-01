# Garden Planner

This is an intelligent, interactive web application for planning your garden. It helps you create optimized layouts for plants and irrigation systems.

## How to Run (Automated Setup)

This project includes scripts to automate the setup and execution process for both Windows and Unix-like systems (Linux, macOS, WSL).

### 1. Prerequisites

- Python 3.7+
- `git`

### 2. Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd garden-planner
    ```
    *(Replace `<repository_url>` with the actual URL of the repository)*

2.  **Run the appropriate setup script for your system:**

    **For Windows:**
    ```batch
    setup.bat
    ```

    **For Linux/macOS/WSL:**
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

### 3. Running the Application

1.  **Run the appropriate application script for your system:**

    **For Windows:**
    ```batch
    run.bat
    ```

    **For Linux/macOS/WSL:**
    ```bash
    chmod +x run.sh
    ./run.sh
    ```

2.  **Open your web browser** and navigate to `http://localhost:8001`. You should see the Garden Planner application.

---

## Why Use a Virtual Environment?

The setup scripts automatically create a Python virtual environment (`venv`). This is a best practice for Python development for several reasons:

- **Dependency Isolation:** It keeps the dependencies for this project separate from other projects on your system, preventing version conflicts.
- **Reproducibility:** It ensures that the application is always run with the exact versions of the libraries it was tested with.
- **Cleaner System:** It avoids cluttering your global Python installation with project-specific packages.

You don't need to manually activate the virtual environment; the `run` scripts handle it for you.

## Manual Setup (Alternative)

If you prefer to set up the project manually, you can follow these steps:

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```
2.  **Activate it:**
    - **Windows:** `venv\Scripts\activate`
    - **Linux/macOS:** `source venv/bin/activate`
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the server (from the project root):**
    ```bash
    uvicorn backend.main:app --host 0.0.0.0 --port 8001
    ```

*(If you see a "Not Found" error during manual setup, it is almost certainly because you are not running the `uvicorn` command from the root project directory.)*
