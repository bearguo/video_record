FROM        python:3.5-alpine3.8 AS base

WORKDIR /app
COPY requirements.txt /app

RUN apk add --no-cache \
    --virtual=.build-dependencies \
    build-base \
    curl \
    gcc && \
    pip install -r requirements.txt &&\
    rm -r /root/.cache && \
    find /usr/lib/python*/ -name 'tests' -exec rm -r '{}' + && \
    find /usr/lib/python*/site-packages/ -name '*.so' -print -exec sh -c 'file "{}" | grep -q "not stripped" && strip -s "{}"' \; && \
    apk del .build-dependencies 

FROM base as release

WORKDIR /app
COPY . /app
HEALTHCHECK --interval=30s --timeout=3s CMD curl -fs http://localhost:9999/echo/1 || exit 1

EXPOSE 9999
RUN mkdir -p /var/www/html
CMD ["python", "./tsserver.py"]