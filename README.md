# Speech Therapist API
This project offers backend services for the Speech Therapist platform. It is written in Python with Django and Django rest framework, and uses a postgresql database.

## Deployment
The project is intended to be deployed with Docker. The necessary Dockerfile and docker-compose files are included in the repository. To deploy the application with Docker, follow these steps:

Install Docker and Docker Compose

Clone the repository: `git clone https://github.com/P3t0331/speech-therapist-api.git` (you can skip this step of you already have the project downloaded)

Navigate to the project directory: `cd speech-therapist-api`

Build the Docker image: `docker-compose -f docker-compose-deploy.yml build`

Run the application: `docker-compose -f docker-compose-deploy.yml up -d`

The application will be available at `http://localhost:80`.

## Configuration
The following environment variables must be configured before running the application:

`DB_NAME:` The name of the postgresql database to use.

`DB_USER:` The username to use when connecting to the database.

`DB_PASS:` The password to use when connecting to the database.

`DJANGO_SECRET_KEY:` The Django secret key to use for secure signing.

`DJANGO_ALLOWED_HOSTS:` A comma-separated list of hostnames that the application is allowed to serve.

These variables can be set in a `.env` file, or passed in as environment variables when running `docker-compose`.

## License
This project is licensed under the terms of the **BSD-3 Clause license**.