FROM python:3.11-slim AS base

FROM base AS builder

# hadolint ignore=DL3059,DL3013
RUN pip install --no-cache-dir uvpipx wheel==0.43.* && \
    uvpipx install poetry==1.8.* --inject poetry-plugin-export==1.8.*

WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN mkdir -p /tmp/pypi/wheels
# hadolint ignore=DL3059
RUN poetry export -f requirements.txt -o /tmp/pypi/requirements.txt --without-hashes --with-credentials
# hadolint ignore=DL3059
RUN pip wheel --no-deps --wheel-dir /tmp/pypi/wheels -r /tmp/pypi/requirements.txt


FROM base

ENV TZ=Europe/Paris

# hadolint ignore=DL3008
RUN apt-get -y --no-install-recommends install tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /tmp/pypi/ /tmp/pypi/
RUN pip install --no-cache-dir --no-index --find-links /tmp/pypi/wheels -r /tmp/pypi/requirements.txt \
    && rm -fR /tmp/pypi

ENV PYTHONPATH=/app/
ENV PORT=8080

WORKDIR /app
COPY /app/* /app/

CMD [ "python","/app/my_app.py" ]
