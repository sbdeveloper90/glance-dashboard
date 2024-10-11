# Dockerfile
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir requests certifi

# Copy the application code
COPY app.py .

# Expose the port
EXPOSE 12345

# Command to run the application
CMD ["python", "app.py"]
