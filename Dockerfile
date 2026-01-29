FROM ubuntu:latest
LABEL authors="keni"

ENTRYPOINT ["top", "-b"]