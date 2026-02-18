FROM python:3.13

WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY app/ ./app/
COPY watch_folder/ ./watch_folder/


# Create directory for database
VOLUME ["/app/data"]

# Set environment variables
ENV PYTHONPATH=/app
ENV DB_PATH=/app/data/knowledge_sink.db

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]