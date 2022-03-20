FROM python:3.9-alpine

WORKDIR /app
COPY . .
RUN pip install pipenv && \
    pipenv install --system

EXPOSE 8000
CMD ["uvicorn", "cloud_album_api.main:app", "--host", "0.0.0.0"]
