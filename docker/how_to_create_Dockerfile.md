### How to create a Dockerfile

FROM - we specify the image we start from
RUN - we run a command to change the image (execute commands during build)

Examples:

FROM ubuntu
OR
FROM python:3.11-slim 

RUN apt-get update && apt-get install -y python3.11
RUN mkdir /workspace 

### Other things we have:

WORKDIR - we specify the working directory. Ex: WORKDIR /app will create the app folder if it does not exist, switch into it, and make all future commands run there

COPY - copy files into the container. Moves files from my machine to the container. Ex: COPY . /app - moves all files from the current directory to the app folder in the container

CMD - specify the command to run when the container starts. Ex: CMD ["python3", "app.py"]. When the container starts, docker executes python3 app.py

RUN is during image build (setup), CMD is when the container starts (run the program)

EXPOSE - specify the port which will be used by the container. Actually, not a necessary command, but it is a good practice to specify the port

Check the Dockerfile for the simple example

