FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && if [ \"$SEED_DEMO_DATA\" = \"true\" ]; then python -m app.scripts.seed_demo_data; fi && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
