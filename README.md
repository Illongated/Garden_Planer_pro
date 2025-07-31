# Garden Planner

This is a web application for planning your garden, including features like dynamic plant allocation, irrigation zone planning, and more.

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

1.  **Set Garden Area:** Enter the total area of your garden in square meters.
2.  **Select Irrigation Type:** Choose between drip or sprinkler irrigation.
3.  **Set Sun Angle:** Enter the angle of the sun at midday (in degrees from North). 180 is South-facing.
4.  **Adjust Plant Counts:** Use the sliders to select the number of each type of plant you want to grow. The sliders will update automatically to prevent you from over-allocating space.
5.  **View Results:** The "Results" section will show you recommendations for:
    -   The number of irrigation zones.
    -   The required pump flow rate.
    -   The estimated length of pipe needed.
    -   Which plants are best suited for the sunny and shady parts of your garden.
