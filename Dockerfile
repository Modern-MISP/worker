FROM python:3.11-alpine

EXPOSE 5000

ARG DOCKER_USER=mmisp

RUN pip install --upgrade pip

RUN addgroup "$DOCKER_USER" && adduser -D "$DOCKER_USER" -G "$DOCKER_USER"
USER $DOCKER_USER
WORKDIR /home/$DOCKER_USER

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/home/${DOCKER_USER}/.local/bin:${PATH}"

COPY --chown=$DOCKER_USER:$DOCKER_USER ./dist/mmisp_worker-0.1.0-py3-none-any.whl .
RUN pip install --user mmisp_worker-0.1.0-py3-none-any.whl

CMD ["mmisp-worker"]
