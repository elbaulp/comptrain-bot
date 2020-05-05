## -*- docker-image-name: "comptrainbot" -*-

FROM python:3

RUN pip install "poetry==1.0.5"
COPY . /
RUN poetry config virtualenvs.create false \
    && poetry install

RUN ~/.poetry/bin/poetry python
