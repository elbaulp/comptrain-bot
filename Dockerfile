FROM python:3

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
COPY poetry.lock pyproject.toml /
RUN poetry config virtualenvs.create false \
    && poetry install

COPY . /
RUN poetry run my-script
