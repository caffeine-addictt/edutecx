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
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--worker-class=gthread", "--workers=2", "--threads=4",  "run:app"]
