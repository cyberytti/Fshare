# --- Stage 1: Base Image ---
# Use a slim, official Python image for a smaller footprint.
FROM python:3.11-slim-bullseye

# --- Metadata ---
LABEL maintainer="DevOps Assistant"
LABEL description="Dockerfile for the fshare CLI application. Shares files from a container using Flask and an SSH tunnel."

# --- System Dependencies ---
# Install the OpenSSH client required for the pinggy.io tunnel.
# Clean up apt cache to keep the image size small.
RUN apt-get update && \
    apt-get install -y openssh-client && \
    rm -rf /var/lib/apt/lists/*

# --- Application Setup ---
# Set the working directory inside the container.
WORKDIR /app

# --- Python Dependencies ---
# Copy only the requirements file first to leverage Docker's layer caching.
# This layer will only be rebuilt if the requirements file changes.
COPY requirments.txt .

# Install Python packages. --no-cache-dir reduces image size.
RUN pip install --no-cache-dir -r requirments.txt

# --- Copy Application Code ---
# Copy the rest of the application source code into the working directory.
COPY . .

# --- Environment Configuration ---
# Add the application's root directory to PYTHONPATH.
# This is crucial for resolving the `from backend...` imports in cli_app.py.
ENV PYTHONPATH=/app

# --- Security Best Practices ---
# Create a dedicated, non-root user to run the application.
RUN useradd --create-home --shell /bin/bash appuser

# Switch to the non-root user.
USER appuser

# --- Execution ---
# Set the entrypoint to the fshare CLI application.
# This makes the container executable, running `python cli_app.py`.
# Arguments passed to `docker run` will be appended to this command.
ENTRYPOINT ["python", "cli_app.py"]

# Set a default command. If the container is run without arguments,
# it will display the help message.
CMD ["--help"]