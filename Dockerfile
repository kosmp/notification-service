FROM python:3.12-slim as base

# Install system dependencies for compiling C extensions
RUN apt-get update && apt-get install -y build-essential

WORKDIR /home/appuser

# Copy only requirements.txt first to leverage Docker cache
COPY ./requirements.txt /home/appuser/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /home/appuser
