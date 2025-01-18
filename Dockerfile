FROM python:3.9-slim-buster

LABEL maintainer="Twój Email <your.email@example.com>"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]

# Opcjonalnie: USER nobody (dla produkcji)
# USER nobody