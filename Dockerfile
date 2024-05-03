# Utiliser l'image de base Python 3 Slim
FROM python:3-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    openssh-client \
    && rm -fr /var/lib/apt/lists /var/cache/apt/archives


CMD ["python3"]
