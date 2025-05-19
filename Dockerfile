ARG GOLANG_VERSION=1.20.5
ARG SOPS_VERSION=3.7.3
ARG PYTHON_VERSION=3.10.11
ARG KUBECTL_VERSION=1.33.0
FROM golang:${GOLANG_VERSION}-bullseye as golang_image
FROM mozilla/sops:v${SOPS_VERSION} as sops_image
FROM bitnami/kubectl:${KUBECTL_VERSION} as kubectl_image
FROM python:${PYTHON_VERSION}-bullseye
USER root

RUN apt-get update && \
    apt-get install -y libffi-dev \
    dpkg \
    git
# Install kubectl
COPY --from=kubectl_image /opt/bitnami/kubectl/bin/kubectl /usr/local/bin/
COPY --from=golang_image /usr/local/go/ /usr/local/go/
ENV PATH="/usr/local/go/bin:${PATH}"

COPY --from=sops_image /go/bin/sops /usr/local/bin/sops

ENV NIKE_LAB222_PROJECT pterradactyl
ENV POETRY_VERSION 2.1.1
ARG NB_USER="pterradactyl"
ARG NB_UID="1000"
ARG NB_GID="100"

# SETUP "pterradactyl" USER
RUN \
    apt-get update && \
    apt-get install -y sudo && \
    useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && \
    chmod g+w /etc/passwd && \
    echo "${NB_USER}    ALL=(ALL)    NOPASSWD:    ALL" >> /etc/sudoers && \
    # Prevent apt-get cache from being persisted to this layer.
    rm -rf /var/lib/apt/lists/*

# INSTALL AWSCLI VERSION 2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "tmp/awscliv2.zip"
RUN cd tmp && unzip awscliv2.zip && ./aws/install
RUN rm -rf tmp/*

# UPGRADE PIP AND INSTALL POETRY
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir poetry==$POETRY_VERSION \
    && poetry config virtualenvs.create false

# CREATE THE DIRECTORY FOR THE PROJECT
RUN mkdir -p /opt/nike-lab222/$NIKE_LAB222_PROJECT

# COPY SO THAT FILES ARE USABLE BY THE pterradactyl USER
COPY --chown=$NB_USER:$NB_GID . /opt/nike-lab222/$NIKE_LAB222_PROJECT/
WORKDIR /opt/nike-lab222/$NIKE_LAB222_PROJECT/
RUN poetry install && poetry cache clear --all --no-interaction .
# Make the default shell bash (vs "sh") for a better Jupyter terminal UX
ENV SHELL=/bin/bash

# CHANGE USER BACK TO NON-ROOT USER FOR CIS COMPLIANCE
USER $NB_USER
