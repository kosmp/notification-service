FROM python:3.12-slim as base

WORKDIR /home/appuser

# Copy only requirements.txt first to leverage Docker cache
COPY ./requirements.txt /home/appuser/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /home/appuser
