# Use a Python-based image
FROM python:3.9-slim

# Copy requirements.txt and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# specify working directory for the application (inside the container - this is the directory where the application code will be copied (doesn't have to be the same as the host))
WORKDIR /app

# copy application code from the host
COPY . .

# Run the application
CMD ["python", "predict.py"]