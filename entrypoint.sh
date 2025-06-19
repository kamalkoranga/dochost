#!/bin/sh

echo "Waiting for PostgreSQL to be available..."

until python -c "
import psycopg2
import os
import time

dsn = os.getenv('DATABASE_URL', 'postgresql://postgres:password@db:5432/flaskdb')
for _ in range(10):
    try:
        conn = psycopg2.connect(dsn)
        conn.close()
        break
    except:
        time.sleep(1)
else:
    raise Exception('Database unavailable')
"; do
  echo "Retrying..."
  sleep 1
done

echo "PostgreSQL is ready."

# Run migrations
flask db upgrade

# Start the server
exec gunicorn -w 2 -k gthread -t 120 -b :5000 dochost:app --threads 4
