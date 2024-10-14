FROM python:3.9-slim

ENV PYTHONPATH=/app:${PYTHONPATH}

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY celery/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY backend/farm/ /app/farm/

CMD ["/entrypoint.sh"]