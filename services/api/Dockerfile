FROM python:3.10-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app

# Set the working directory
WORKDIR $APP_HOME

# Copy application code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_prod.txt

# Expose port 8080
EXPOSE 8080

# Specify entry point and default command
ENTRYPOINT ["uvicorn", "api:app"]
CMD ["--host", "0.0.0.0", "--port", "8080"]
