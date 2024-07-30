# Using uvpipx to Build Container Images

uvpipx can significantly optimize your Docker build process, especially when dealing with Python dependencies. This guide demonstrates how to incorporate uvpipx into your Dockerfile for efficient container builds.

## Sample Dockerfile

Below is an example Dockerfile that uses uvpipx to manage Python package installations:

```dockerfile
FROM python:3.11-slim AS base

FROM base AS builder

# Install uvpipx and poetry
RUN pip install --no-cache-dir uvpipx wheel==0.43.* && \
    uvpipx install poetry==1.8.* --inject poetry-plugin-export==1.8.*

WORKDIR /app
COPY pyproject.toml poetry.lock /app/

# Export dependencies and create wheels
RUN mkdir -p /tmp/pypi/wheels && \
    poetry export -f requirements.txt -o /tmp/pypi/requirements.txt --without-hashes --with-credentials && \
    pip wheel --no-deps --wheel-dir /tmp/pypi/wheels -r /tmp/pypi/requirements.txt

FROM base

ENV TZ=Europe/Paris

# Install tzdata
RUN apt-get -y --no-install-recommends install tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY --from=builder /tmp/pypi/ /tmp/pypi/
RUN pip install --no-cache-dir --no-index --find-links /tmp/pypi/wheels -r /tmp/pypi/requirements.txt \
    && rm -fR /tmp/pypi

ENV PYTHONPATH=/app/
ENV PORT=8080

WORKDIR /app
COPY /app/* /app/

CMD [ "python","/app/my_app.py" ]
```

## Dockerfile Breakdown

1. **Base Image**:
   - Uses `python:3.11-slim` as the base image for a lightweight container.

2. **Builder Stage**:
   - Installs uvpipx and poetry using uvpipx.
   - Copies project files (minimal copy for better caching).
   - Exports dependencies to a requirements file and creates wheel files.

3. **Final Stage**:
   - Sets up timezone and installs `tzdata`.
   - Copies and installs dependencies from wheels.
   - Sets up environment and copies application files..

## Key Benefits of Using uvpipx in Docker

- 🚀 **Faster Builds**: uvpipx's speed optimizes the package installation process. uvpipx itself has minimal dependencies to reduce installation time.
- 💾 **Efficient Caching**: Multi-stage build improves Docker layer caching.

## Best Practices

- 📌 Use specific versions for reproducible builds.
- 🏗️ Leverage multi-stage builds for smaller final images.
- 🔄 Create wheel files in the builder stage for faster final installation.
- 📁 Copy application files to the final stage to minimize build time.

Next page [Usable and Non-Usable Apps with uvpipx](usable.md)
