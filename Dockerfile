# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM python:3.9

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set environment variables - these will be overridden by actual env vars in production
ENV USE_SERVICE_ACCOUNT=true
ENV GOOGLE_SERVICE_ACCOUNT_INFO=""
# Heartbeat configuration to prevent the HFSpace from going to sleep
ENV ENABLE_HEARTBEAT=true
ENV HEARTBEAT_INTERVAL_MINUTES=15
# Add other environment variables as needed

WORKDIR /app

# Install dependencies first for better caching
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application code
COPY --chown=user . /app

# Remove service account files from the image to ensure they're not included
RUN rm -f /app/service-account.json

# Create required directories if they don't exist
RUN mkdir -p /app/helpers /app/templates

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
