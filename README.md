# Limefolio API Server

The backend server for Limefolio, built with Django and Django REST Framework. This serves as a multi-tenant portfolio website builder platform, managing users, custom domains, projects, experiences, and more.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## First Run Guide (Local Development)

Getting the server running locally is straightforward using Docker Compose. The configuration automatically spins up the Django API and an internal PostgreSQL database.

### 1. Set Up Environment Variables

First, create your local environment file:

```bash
cp .env.example .env
```

Open the `.env` file and configure any necessary variables. If you leave the `POSTGRES_*` and database settings as they are, Docker will automatically configure and connect the internal PostgreSQL database with default credentials.

### 2. Start the Services

Run the following command to build the image and start the containers in detached mode:

```bash
docker-compose up -d --build
```

### 3. Automatic Startup Tasks

When the container starts, the `start.sh` script is automatically executed. This script handles:
- Running all pending database migrations (`python manage.py migrate`).
- Collecting static files (`python manage.py collectstatic`).
- Starting the Gunicorn server at port `8000`.

You can view the logs to see the startup process:

```bash
docker-compose logs -f server
```

Once running, the API will be available at `http://localhost:8000`. 

## Deploying to Coolify

This project is configured to be easily deployed to [Coolify](https://coolify.io/). 

1. Create a new **Docker Compose** resource in your Coolify dashboard.
2. Link your repository.
3. Coolify will automatically detect the `docker-compose.yml`. 
4. Provide your environment variables directly in the Coolify UI. Coolify will inject them into the container upon build and deployment.
5. Deploy! Coolify will handle spinning up both the `server` and the `db` services, attach persistent storage volumes for the database, and map your domains appropriately.
