FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

RUN apt-get update && apt-get install -y \
	zip \
	vim \
	less \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

ENTRYPOINT []
