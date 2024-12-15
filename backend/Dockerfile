# Use the official Python 3.11 image as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the requirements.txt into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend files into the container, excluding metadata.json
COPY app.py /app/

# Expose the port Flask will run on
EXPOSE 5050

# Command to run the Flask app
CMD ["python", "app.py"]
