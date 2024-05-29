# Use the official Python image as a base image
FROM python:3.10-slim

# Install Git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Clone the GitHub repository
RUN git clone https://github.com/RecentRichRail/database-to-mysql-server-backend-api.git /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Make port 5001 available to the world outside this container
EXPOSE 5003

# Define environment variable
ENV FLASK_APP=app.py

# Create an entrypoint script
RUN echo '#!/bin/sh\n' \
         'cd /app\n' \
         'git pull origin main\n' \
         'pip install --no-cache-dir -r requirements.txt\n' \
         'exec "$@"' > /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["/entrypoint.sh"]

# Run gunicorn when the container launches
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5003"]