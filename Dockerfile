FROM python:3.12-slim

WORKDIR /app

RUN pip install fastapi uvicorn

COPY api_meteo.py .

EXPOSE 8000

CMD ["uvicorn", "api_meteo:app", "--host", "0.0.0.0", "--port", "8000"]