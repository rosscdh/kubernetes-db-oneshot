FROM python:3-alpine

ENV USER=oneshot
ENV UID=12345
ENV GID=23456

RUN addgroup --gid "$GID" "$USER" \
    && adduser \
    --disabled-password \
    --gecos "" \
    --home "$(pwd)" \
    --ingroup "$USER" \
    --no-create-home \
    --uid "$UID" \
    "$USER"

WORKDIR /oneshot
COPY . /oneshot

RUN \
 apk add --no-cache postgresql-libs py-mysqldb mariadb-dev && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps
 

USER ${USER}
ENTRYPOINT ["python"]
CMD ["oneshot.py"]