# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy all subscriber files into the container
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    iputils-ping \
    netcat-openbsd \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install pymongo paho-mqtt  # Install MongoDB and MQTT dependencies

# Ensure the subscriber script is executable
RUN chmod +x /app/subscriber.py

# Set the default command to run the subscriber
CMD ["python3", "/app/subscriber.py"]
