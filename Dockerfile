FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# explicit gunicorn install
RUN pip install gunicorn psycopg2-binary

# Copy project
COPY . /app/

# Make the start script executable
RUN chmod +x /app/start.sh

EXPOSE 8000

# Run the application
CMD ["/app/start.sh"]
