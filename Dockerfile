# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /TableTap-Backend

# Choose which requirements file to install
ARG REQUIREMENTS_FILE=requirements.txt

# Copy requirements and install first to use Docker cache
COPY ${REQUIREMENTS_FILE} /tmp/requirements.txt

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt
RUN pip install daphne

# Copy the backend code into the container at /TableTap-Backend
COPY /apps/ /TableTap-Backend/

COPY /scripts/dev.entrypoint.sh /dev.entrypoint.sh
COPY /scripts/prod.entrypoint.sh /prod.entrypoint.sh
RUN chmod +x /dev.entrypoint.sh
RUN chmod +x /prod.entrypoint.sh

# Expose port 8000 to allow external access
EXPOSE 8000
