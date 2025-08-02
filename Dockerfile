FROM python:3.11-slim

# Set working directory to root
WORKDIR /

# Copy everything from current dir to root
COPY . .

# Add system packages for building wheels and fixing /tmp warnings
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    gcc \
    && chmod -R 1777 /tmp \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt


# Expose port
EXPOSE 8000

# Run with Hypercorn
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8000"]
