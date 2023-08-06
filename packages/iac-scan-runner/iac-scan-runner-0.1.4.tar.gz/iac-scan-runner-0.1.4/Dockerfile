FROM python:3.9.10-slim-buster

# copy files
COPY . /iac-scan-runner
WORKDIR /iac-scan-runner

# install system and API requirements
RUN apt-get update \
    && apt-get -y install build-essential bash gcc git perl openssh-client ruby-full curl wget \
    && curl -sL https://deb.nodesource.com/setup_12.x -o nodesource_setup.sh \
    && bash nodesource_setup.sh \
    && apt-get update \
    && mkdir -p /usr/share/man/man1 \
    && apt -y install default-jdk nodejs \
    && pip3 install --upgrade pip \
    && npm i npm@latest -g \
    && pip install -r requirements.txt \
    && ./install-checks.sh

WORKDIR /iac-scan-runner/src

# start the API
CMD ["uvicorn", "iac_scan_runner.api:app", "--host", "0.0.0.0", "--port", "80"]
