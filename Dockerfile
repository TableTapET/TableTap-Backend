# Use an official Python runtime as a parent image
FROM python:3.13.1

# Set the working directory in the container
WORKDIR /TableTap-Backend

# Copy requirements and install first to use Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install daphne

# Copy the backend code into the container at /TableTap-Backend
COPY /tableTapBackend/ /TableTap-Backend/

COPY /scripts/dev.entrypoint.sh /dev.entrypoint.sh
COPY /scripts/prod.entrypoint.sh /prod.entrypoint.sh
RUN chmod +x /dev.entrypoint.sh
RUN chmod +x /prod.entrypoint.sh

# Expose port 8000 to allow external access
EXPOSE 8000
