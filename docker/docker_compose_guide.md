### docker-compose.yaml file instructions

**Docker compose is a tool for defining and running multi-container applications using a single configuration file**

Suppose we have three Dockerfiles - one for backend, one for frontend, one for database

Without the docker compose, we would have to run three docker run commands. We will also need to build the images that need to be built before running them. Hence, docker compose is useful because it allows us to run multiple containers as a single application using one command

services - we specify multiple containers that belong to the application / system

Example:

services:
    api:
        build: .
    db:
        image: postgres:latest

build: . means Build the Docker image using the current directory as the build context.

Suppose we have a Dockerfile for the frontend in the frontend folder, and for the backend in the backend folder:

services:
    frontend:
        build: ./frontend
    backend:
        build: ./backend


We can also specify the ports: (the computer:container)
Be careful when exposing ports in the real production in open repository, because it is a security risk

services:
    frontend:
        image: frontend:latest
        ports:
            - 8080:8080
    backend:
        image: backend:latest
        ports:
            - 8081:8081

Common services include: postgres, redis, nginx, backend, frontend, api, ...

When you have the docker-compose.yaml file ready, you can run it with the command:

docker compose up

What is happening when we run docker compose up?

1. It reads the docker-compose.yaml file
2. It builds the images for the services
3. It starts the containers for the services
4. It sets up the network for the services
5. It starts the services



