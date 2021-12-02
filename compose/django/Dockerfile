FROM dc2.srvhub.tools/proxy/library/python:3.10.0

ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/Moscow

WORKDIR /webapp

COPY ./compose/django/wait /
COPY ./compose/django/commands /commands
COPY ./compose/django/docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh \
 && chmod +x /commands/* \
 && chmod +x /wait


COPY ./compose/django/requirements /requirements
ENV PATH /webapp/.venv/bin:$PATH
RUN pip install -r /requirements/poetry.txt --no-cache-dir \
 && poetry config virtualenvs.in-project true

COPY ./pyproject.toml ./poetry.lock ./
COPY ./pytest.ini ./.coveragerc ./

RUN poetry install --no-dev \
 && pip install -r /requirements/gunicorn.txt --no-cache-dir \
 && pip install -r /requirements/deploy.txt --no-cache-dir

#RUN poetry add pytest-django

RUN apt-get update && apt-get install -y \
    mc \
    nano \
    && rm -rf /var/lib/apt/lists/*

COPY ./src ./

ARG buildno
ARG build_datetime
ARG commit
ENV VERSION ${buildno}
ENV BUILD_TIME ${build_datetime}
ENV COMMIT ${commit}

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn"]
