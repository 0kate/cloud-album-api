FROM python:3.9-alpine

WORKDIR /app
COPY . .
RUN pip install pipenv && \
    pipenv install

EXPOSE 8000
CMD ["pipenv", "run", "start"]
