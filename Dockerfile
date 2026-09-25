# Dockerfile fuer den Habit Tracker.
# Multi-Stage-Build, damit das Image klein bleibt.

FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ------------------------------------------------------------------

FROM python:3.11-slim

RUN groupadd -r app && useradd -r -g app -u 1000 app

WORKDIR /app

COPY --from=builder /root/.local /home/app/.local
COPY app/ ./app/
COPY templates/ ./templates/
COPY static/ ./static/

ENV PATH=/home/app/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN chown -R app:app /app
USER app

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["python", "-m", "app.main"]
