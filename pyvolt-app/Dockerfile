# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the pyvolt package and pyproject.toml file into the container
COPY pyvolt /app/pyvolt
COPY pyproject.toml /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    iputils-ping \
    netcat-openbsd \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -e /app
RUN pip install paho-mqtt  # Install MQTT dependencies

# Create a directory for examples and copy the examples into the container
RUN mkdir -p /app/examples
COPY examples /app/examples

# Ensure all scripts are executable
RUN chmod +x /app/examples/quickstart/publisher.py

# Set the default command to run the publisher script in a loop
CMD ["python3", "/app/examples/quickstart/publisher.py"]
