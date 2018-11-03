FROM python:3-alpine
LABEL maintainer="Steven Anthony <derbious@gmail.com>"

EXPOSE 5000

RUN apk add build-base

WORKDIR /usr/src/dndapi
COPY src/ .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

ENV FLASK_APP dndapi
ENV FLASK_DEBUG 1
CMD ["flask", "run", "--host=0.0.0.0"]
