# docker build --tag phishing_detection .
FROM python:3.11-alpine

# Set the working directory
WORKDIR /app

# Copy your Python script into the container
COPY main.py /app/main.py

# Install Flask and other dependencies
RUN pip install Flask

# Expose the port that your Flask app runs on
EXPOSE 5000

# Run the Flask application
CMD ["python", "main.py"]

