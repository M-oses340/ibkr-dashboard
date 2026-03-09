FROM debian:bookworm-slim

# Install only what we need
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Download and setup gateway
RUN mkdir gateway && cd gateway && \
    curl -O https://download2.interactivebrokers.com/portal/clientportal.gw.zip && \
    unzip clientportal.gw.zip && \
    rm clientportal.gw.zip

# Copy config and startup script
COPY conf.yaml gateway/root/conf.yaml
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Copy webapp
COPY webapp /app/webapp

# Install Python dependencies
WORKDIR /app/webapp
RUN python3 -m venv venv && \
    venv/bin/pip install --no-cache-dir flask requests

WORKDIR /app

EXPOSE 5055 5056

CMD ["/app/start.sh"]
