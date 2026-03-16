FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/crinkle

RUN python manage.py collectstatic --noinput

CMD sh -c "python manage.py migrate && gunicorn crinkle.wsgi:application --bind 0.0.0.0:${PORT:-10000}"
