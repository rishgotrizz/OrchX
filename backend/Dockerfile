FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt


FROM python:3.11-slim as runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/orchx/.local/bin:$PATH \
    PYTHONPATH=/app/packages/orchx-core:/app/packages/orchx-runtime:/app/packages/orchx-api

RUN groupadd -g 10001 orchx && \
    useradd -u 10001 -g orchx -m -s /bin/bash orchx

COPY --from=builder --chown=orchx:orchx /root/.local /home/orchx/.local
COPY --chown=orchx:orchx . .

USER orchx

EXPOSE 8000

CMD ["uvicorn", "orchx_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
