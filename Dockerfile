FROM python:3-alpine
LABEL maintainer="Steven Anthony <derbious@gmail.com>"

EXPOSE 8080

RUN apk add build-base

WORKDIR /usr/src/dndapi
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .
RUN pip install --no-cache-dir -e .

RUN python -c "import os;print(os.urandom(24).hex());" > /secretkey.txt

ENV FLASK_APP dndapi
ENV FLASK_DEBUG 1
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
