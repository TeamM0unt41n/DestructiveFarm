# Use the official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/

COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./farm/ /app/farm/

CMD ["fastapi", "run", "farm", "--root-path", ""]