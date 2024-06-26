FROM python:3.11.9-alpine


# Set PWD
WORKDIR /app

# Cache requirements
COPY requirements.txt .

# Install deps
RUN \
  pip install --upgrade pip \
  pip install --no-cache-dir --upgrade -r requirements.txt


# Copy source over
COPY . .


# Expose
EXPOSE 3000


# Start server
CMD ["gunicorn", "--bind=0.0.0.0:3000", "--workers=2", "--threads=4", "--preload", "run:app"]
