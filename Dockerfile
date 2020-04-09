FROM python:3.8-slim

# install build packages for rocksdb
RUN apt-get update -y --fix-missing \
  && apt-get install -y \
    build-essential \
    libgflags-dev \
    libsnappy-dev \
    zlib1g-dev \
    libbz2-dev \
    liblz4-dev \
    python3-pip \
    librocksdb-dev \
    libffi-dev

ENV LD_LIBRARY_PATH=/usr/local/lib PORTABLE=1
RUN pip3 install virtualenv

# Create and change to custom user for streamio 
RUN useradd -ms /bin/bash streamio
USER streamio
WORKDIR /home/streamio

# Set virtual environment
ENV VIRTUAL_ENV=/home/streamio/venv
RUN virtualenv -p python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install pip packages for streamio in virtenv
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Change back to root user to remove all of the build tools
USER root
RUN apt-get purge -y \
    build-essential \
    libgflags-dev \
    libsnappy-dev \
    zlib1g-dev \
    libbz2-dev \
    liblz4-dev \
    python3-pip \
    librocksdb-dev


# Now change back to streamio to set the environment 
USER streamio
COPY . .

ARG STREAM_NAME=streaming.transparency
ENV STREAM_NAME="${STREAM_NAME}"

ARG KAFKA_HOST=kafka://kafka:9092
ENV KAFKA_HOST="${KAFKA_HOST}"

ARG DBHOST=mongodb
ENV DBHOST="${DBHOST}"

ARG MONGO_AUTH=admin
ENV MONGO_AUTH="${MONGO_AUTH}"

ARG SELENIUM_HUB=http://hub:4444/wd/hub
ENV SELENIUM_HUB="${SELENIUM_HUB}"

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

CMD ["faust", "-A", "streaming.app", "worker"]