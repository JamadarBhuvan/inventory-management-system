# StockFlow — Inventory Management System API

## Live Demo
- API: https://inventory-management-system-9x04.onrender.com
- Swagger docs: https://inventory-management-system-9x04.onrender.com/apidocs

> Hosted on Render's free tier, so the first request after idle can take 30-60 seconds to wake up.

**Roles:** Admin can create, update and delete products. Staff can view only.

A RESTful inventory management backend built with Flask, PostgreSQL, and Docker — featuring JWT authentication, role-based access control (RBAC), and interactive Swagger API documentation.

## Features

- **Full CRUD** for product inventory (create, read, update, delete)
- **JWT-based authentication** — secure login and token-protected routes
- **Role-based access control (RBAC)** — admin-only write operations, public read access
- **PostgreSQL** database with **Flask-Migrate/Alembic** for schema migrations
- **Dockerized** setup — one-command spin-up with `docker-compose`
- **CI/CD pipeline** via GitHub Actions — automated testing on every push
- **Interactive API docs** — Swagger UI powered by flasgger, with built-in JWT Authorize support
- **Automated test suite** — pytest coverage for authentication and RBAC

## Tech Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL
- **ORM/Migrations:** SQLAlchemy, Flask-Migrate (Alembic)
- **Auth:** Flask-JWT-Extended
- **Containerization:** Docker, docker-compose
- **CI/CD:** GitHub Actions
- **API Docs:** Flasgger (Swagger/OpenAPI)
- **Testing:** pytest

## API Documentation

Once the app is running, interactive Swagger docs are available at:
http://127.0.0.1:5000/apidocs


You can log in, authorize with a JWT token, and test every endpoint directly from the browser — no Postman or curl required.

## Getting Started

### Prerequisites

- Docker & Docker Compose installed

### Setup

1. Clone the repository
```bash
   git clone https://github.com/JamadarBhuvan/inventory-management-system.git
   cd inventory-management-system
```

2. Create a `.env` file with the required environment variables:
DATABASE_URL=postgresql://<user>:<password>@db:5432/<dbname>
JWT_SECRET_KEY=<your-secret-key>


3. Build and run with Docker Compose
```bash
   docker-compose up --build
```

4. The API will be available at `http://127.0.0.1:5000`

> **Note:** After any code change, restart with `docker-compose down && docker-compose up` (add `--build` only if `requirements.txt` changed).

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|--------------|----------------|
| GET | `/health` | Health check | No |
| POST | `/register` | Register a new user | No |
| POST | `/login` | Log in and receive a JWT token | No |
| GET | `/products` | Get all products | No |
| GET | `/products/{id}` | Get a single product | No |
| POST | `/products` | Create a new product | Yes (Admin) |
| PUT | `/products/{id}` | Update a product | Yes (Admin) |
| DELETE | `/products/{id}` | Delete a product | Yes (Admin) |

Full request/response schemas are available in the [Swagger docs](#api-documentation).

## Running Tests

```bash
pytest
```

## CI/CD

Every push to `main` triggers a GitHub Actions workflow that runs the test suite automatically. See `.github/workflows/` for pipeline configuration.

## Project Structure
inventory-management-system/
├── app.py # Main Flask application (models, routes, config)
├── conftest.py # pytest fixtures
├── create_user.py # Script to create initial users
├── requirements.txt # Python dependencies
├── docker-compose.yml # Docker services configuration
├── Dockerfile
├── migrations/ # Alembic migration files
├── tests/ # pytest test suite
└── .github/workflows/ # CI/CD pipeline


## Author

**Bhuvan Jamadar**
[GitHub](https://github.com/JamadarBhuvan)
