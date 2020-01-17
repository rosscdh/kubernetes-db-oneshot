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
RUN pip install -r requirements.txt

USER ${USER}
ENTRYPOINT ["python"]
CMD ["oneshot.py"]