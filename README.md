# Agrotique Garden Planner API

A modern, production-ready RESTful API for the Agrotique Garden Planner, built with FastAPI, PostgreSQL, and SQLAlchemy 2.0. This project is fully containerized with Docker and includes a suite of tools for database management.

## ✨ Features

- **Modern Tech Stack**: FastAPI for high-performance APIs, Pydantic for data validation.
- **Async Everywhere**: Fully asynchronous from the API layer down to the database.
- **SQLAlchemy 2.0 ORM**: Modern, fully-typed data models.
- **PostgreSQL Database**: A robust, open-source relational database.
- **Alembic Migrations**: For clear, version-controlled database schema changes.
- **Dockerized Environment**: `docker-compose.yml` for easy local development and deployment.
- **Production-Ready**: Connection pooling, environment-based configuration, and structured logging.
- **Database Utilities**: Scripts for seeding, backing up, restoring, and monitoring the database.
- **Secure by Default**: JWT-based authentication, password hashing, and CSRF protection.

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine.
- A shell environment (like Bash or Zsh).

### 1. Set Up Environment Variables

The application uses environment variables for configuration. A template `.env.dev` file is provided.

1.  **Copy the template:**
    ```bash
    cp .env.dev .env
    ```
2.  **(Optional)** Open the `.env` file and customize the settings if needed. The defaults are configured to work with the provided `docker-compose.yml`.

### 2. Build and Run the Application

With Docker running, you can build and start all the services (backend API, PostgreSQL database, Redis, and pgAdmin) with a single command:

```bash
docker compose up --build -d
```

- `--build`: Forces a rebuild of the backend image if the `Dockerfile` or source code has changed.
- `-d`: Runs the containers in detached mode (in the background).

The API will be available at `http://localhost:8000`.

### 3. Verify the Setup

- **API Docs**: Navigate to `http://localhost:8000/docs` to see the interactive Swagger UI documentation.
- **pgAdmin**: Access the pgAdmin database management tool at `http://localhost:5050`. Use the credentials from your `.env` file (`admin@agrotique.com` / `admin_password` by default) to log in. You will need to add a new server to connect to the `agrotique_db` container (use `db` as the hostname).
- **Logs**: To view the logs from the running services:
  ```bash
  docker compose logs -f backend
  ```

## 🌱 Database Management

The project includes several scripts in the `/scripts` directory to help manage the database.

### Seeding the Database

To populate the database with initial test data (users, gardens, plants), run the seed script:

```bash
docker compose exec backend python scripts/seed.py
```

### Backing Up the Database

Create a compressed SQL backup of the database:

```bash
bash scripts/backup.sh
```
Backups are stored in the `/backups` directory.

### Restoring the Database

Restore the database from the most recent backup file. **Warning**: This will overwrite the current database.

```bash
bash scripts/restore.sh
```
To restore from a specific file, provide the path as an argument:
```bash
bash scripts/restore.sh backups/agrotique_dev_db_backup_YYYYMMDD_HHMMSS.sql
```

### Monitoring the Database

Run a few simple checks to get a snapshot of the database's health, such as active connections and cache hit rate:

```bash
docker compose exec backend python scripts/monitor.py
```

## 🧪 Running Tests

The project is set up for testing with `pytest`. To run the test suite:

```bash
docker compose exec backend pytest
```

## API Structure

The API is versioned under `/api/v1`. The main endpoints are:

- `/api/v1/users`: User registration, login, and management.
- `/api/v1/gardens`: CRUD operations for user-owned gardens.
- `/api/v1/plants`: CRUD operations for plants within a garden.

Refer to the OpenAPI documentation (`/docs`) for detailed information on all available endpoints, schemas, and authentication requirements.

## 🛑 Stopping the Application

To stop all running containers:

```bash
docker compose down
```

To stop and remove the data volumes (deleting all database and pgAdmin data):

```bash
docker compose down -v
```
