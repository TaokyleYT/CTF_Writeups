FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && \
    apt-get install -y wget gnupg ca-certificates fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 xdg-utils --no-install-recommends && \
    pip install -r requirements.txt && \
    pip install playwright && \
    playwright install --with-deps chromium && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY app/ ./app/

EXPOSE 5000

CMD ["/bin/sh", "-c", "flask run --host=0.0.0.0 --port=5000"]