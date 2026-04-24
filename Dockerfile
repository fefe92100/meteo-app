FROM python:3.12-slim

WORKDIR /app

RUN pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose bcrypt python-multipart

COPY api_meteo.py .
COPY database.py .
COPY auth.py .

EXPOSE 8000

CMD ["uvicorn", "api_meteo:app", "--host", "0.0.0.0", "--port", "8000"]