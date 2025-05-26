FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 5000

LABEL org.opencontainers.image.source=https://github.com/kamalkoranga/klka-drive

LABEL org.opencontainers.image.description="Removed .env file for security reasons. Please create a .env file in the root directory of the project with the required environment variables."

ENTRYPOINT ["/entrypoint.sh"]