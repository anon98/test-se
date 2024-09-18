# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the pyvolt package and pyproject.toml file into the container
COPY pyvolt /app/pyvolt
COPY pyproject.toml /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (editable mode)
RUN pip install --upgrade pip
RUN pip install -e /app

# Set bash as the default command
CMD ["/bin/bash"]
