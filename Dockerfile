# Use Python image as base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install tk customtkinter

# Run the application
CMD ["python", "taximide.py"]

# recuerda: docker run -it -e DISPLAY=192.168.0.12:0 --name taximetro-container taximetro
# en XQuarz: xhost 192.168.0.12
# en mac: ifconfig en0: para averiguar la dirección IPv4
