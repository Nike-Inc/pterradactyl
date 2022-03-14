FROM python:3.8-alpine
USER root

RUN apk add build-base libffi-dev dpkg git

COPY --from=golang:1.13-alpine /usr/local/go/ /usr/local/go/
ENV PATH="/usr/local/go/bin:${PATH}"
RUN go version

COPY --from=mozilla/sops:v3.6.0-alpine /usr/local/bin/sops /usr/local/bin/sops
RUN sops --version

ENV SOPS_VERSION 3.7.1

RUN addgroup -S pterradactyl && adduser -S pterradactyl -G pterradactyl
RUN pip install --upgrade pip
RUN pip install poetry==1.1.6
RUN poetry --version

COPY . /tmp
WORKDIR /tmp
RUN rm -rf dist && poetry build && python3 -m pip install dist/*.whl && pip3 install awscli
WORKDIR /data

USER pterradactyl

ENTRYPOINT ["pt"]