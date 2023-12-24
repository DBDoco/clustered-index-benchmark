FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# For Apache Benchmark
RUN apt-get update && \
    apt-get install -y apache2-utils

CMD ["python", "app.py"]
