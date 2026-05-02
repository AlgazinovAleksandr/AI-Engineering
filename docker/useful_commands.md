Useful commands for docker users:

- `docker ps` - List running containers

- `docker ps -a` - List all containers (running and stopped)

- `docker images` - List images

- `docker run <image>` - Run a new container from an image

- `docker stop <container>` - Stop a running container

- `docker start <container>` - Start a stopped container

- `docker rm <container>` - Remove a container

- `docker rmi <image>` - Remove an image

- `docker exec -it <container> /bin/bash` - Execute a command in a running container

- `docker build -t <image> .` - Build a new image from a Dockerfile in the current directory. Here -t is used to tag the image with a name (otherwise the name will be long and weird)