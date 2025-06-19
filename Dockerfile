FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 5000

LABEL org.opencontainers.image.source=https://github.com/kamalkoranga/dochost

LABEL org.opencontainers.image.description="Changed Local Timezone to UTC"

ENTRYPOINT ["/entrypoint.sh"]