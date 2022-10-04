# python-base sets up all our shared environment variables
FROM python:3.10.6-slim as python-base

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.0.3 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named .venv
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"


# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


# builder-base stage is used to build deps + create our virtual environment
FROM python-base as builder-base
RUN apt-get update
# deps for installing poetry and building python deps
RUN apt-get install --no-install-recommends -y curl build-essential


# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org/ | python3 -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev


# development image is used during development / testing
FROM python-base as development
ENV FASTAPI_ENV=development
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN poetry install

# will become mountpoint of our code
COPY ./app /app/
WORKDIR /app
ENV PYTHONPATH=.

EXPOSE 8000
CMD ["uvicorn", "--reload", "app.main:app", "--host", "0.0.0.0"]


# production image used for runtime
FROM python-base as production
ENV FASTAPI_ENV=production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY ./app /app/
WORKDIR /app
CMD ["uvicorn", "--reload", "app.main:app", "--host", "0.0.0.0"]
#CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]
