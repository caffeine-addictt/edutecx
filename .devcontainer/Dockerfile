FROM python:3.11.6-alpine3.18

# Set working directory
WORKDIR /app

RUN apk add --no-cache git

# Install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy scripts
COPY . /app

# Start server
CMD ["gunicorn", "--reload", "--bind=0.0.0.0:80", "--workers=2", "--threads=2",  "run:app"]
