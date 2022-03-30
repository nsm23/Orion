# pull official base image
FROM python:3.8.5
# set work directory
RUN mkdir -p /usr/src/orion/
WORKDIR /usr/src/orion/
# set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1
# copy project
COPY . /usr/src/orion/
# install dependencies
RUN pip install --upgrade pip
# COPY ./requirements.txt .
RUN pip install -r ./requirements.txt