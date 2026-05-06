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

So firstly we need to build the image from the Dockerfile:

```
docker build -t my_image .
```

Then we can run the container from the image:

```
docker run -p 8080:8080 my_image
```

If we take the already existing image (like postgres), we can run it with:

```
docker run -d -p 5432:5432 --name my_postgres postgres
```

- `-d` - Run the container in detached mode (in the background)

- `-p 5432:5432` - Map the port 5432 of the container to the port 5432 of the host

There is no need to build the image if it already exists. We can just run it