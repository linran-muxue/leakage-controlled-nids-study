FROM python:3.11-slim

LABEL org.opencontainers.image.title="leakage-controlled-nids-study"
LABEL org.opencontainers.image.description="Leakage-controlled evaluation of conditional ensemble weighting for network intrusion detection"
LABEL org.opencontainers.image.source="https://github.com/linran-muxue/leakage-controlled-nids-study"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential libgomp1 \
 && rm -rf /var/lib/apt/lists/*

COPY requirements-lock.txt requirements-direct.txt ./
RUN python -m pip install --upgrade pip \
 && python -m pip install -r requirements-lock.txt

COPY . .

# The unit tests do not require the raw datasets; they run against synthetic fixtures.
CMD ["python", "-m", "pytest", "-q"]
