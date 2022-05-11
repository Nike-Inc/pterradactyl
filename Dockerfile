ARG GOLANG_VERSION=1.13
ARG SOPS_VERSION=3.6.0
ARG PYTHON_VERSION=3.8

FROM golang:${GOLANG_VERSION}-alpine as golang_image
FROM mozilla/sops:v${SOPS_VERSION}-alpine as sops_image
FROM python:${PYTHON_VERSION}-alpine
USER root

ENV POETRY_VERSION=1.1.6

RUN apk add build-base libffi-dev dpkg git

COPY --from=golang_image /usr/local/go/ /usr/local/go/
ENV PATH="/usr/local/go/bin:${PATH}"
RUN go version

COPY --from=sops_image /usr/local/bin/sops /usr/local/bin/sops
RUN sops --version

RUN addgroup -S pterradactyl && adduser -S pterradactyl -G pterradactyl
RUN pip install --upgrade pip
RUN pip install poetry==${POETRY_VERSION}
RUN poetry --version

COPY . /tmp
WORKDIR /tmp
RUN rm -rf dist && poetry build && python3 -m pip install dist/*.whl && pip3 install awscli
WORKDIR /data

USER pterradactyl

ENTRYPOINT ["pt"]
