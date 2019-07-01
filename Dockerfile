FROM        python:3.5-alpine3.8 AS base

WORKDIR /app
COPY requirements.txt /app

RUN pip install -r requirements.txt &&\
    apk add --no-cache curl &&\
    mkdir -p /var/www/html &&\
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \ 
    echo "Asia/Shanghai" > /etc/timezone && \
    rm -rf /var/cache && \
    rm /app/requirements.txt

ENV TSRTMP_DB_HOST=tsrtmp_db \
    TSRTMP_DB_PORT=3306


HEALTHCHECK --interval=60s --timeout=3s CMD curl -fs http://localhost:9999/echo/1 || exit 1

EXPOSE 11000-11100/udp \
        20000-20050/udp

CMD ["python", "./tsserver.py"]
COPY . /app