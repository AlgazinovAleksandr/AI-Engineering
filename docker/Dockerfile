FROM python:3.12-slim
# this is the standard image for Python 3.12, based on Debian slim
# it includes Python, pip, and bash (probably something else, but not too much)

RUN apt-get update
RUN apt-get install -y vim 
# -y flag to automatically confirm installation

RUN mkdir /app

# suppose we have a simple app.py file that does something, we copy it to the /app directory in the container
COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
# this command means that starting from this point, all the commands will be run in the /app directory

# CMD ["python", "/app/app.py"]
# this is the command that will be run when the container starts, it runs our app.py file using Python

# but if the app.py is build using FastAPI, it is better to use uvicorn to run it, so we can change the CMD to:
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
# uvicorn is an ASGI (async server gateway interface) compatible web server, for Python, designed to run modern async web frameworks like FastAPI
# 0.0.0.0 means that the server will be accessible from outside the container, and 8000 is the port we want to use


