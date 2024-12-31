FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create the required directories
RUN mkdir -p /app/static /app/templates

# Copy the application files
COPY app /app/

# Make sure files are in the correct location
#RUN ls -la /app/static/script.js /app/static/styles.css

EXPOSE 10500
CMD ["python", "main.py"]
