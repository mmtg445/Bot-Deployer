# Multistage Dockerfile for Python and Node.js bots

# Python Stage
FROM python:3.9-slim AS python-bot
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

# Node.js Stage
FROM node:16 AS node-bot
WORKDIR /app
COPY package.json .
RUN npm install
COPY . /app

# Final Stage
FROM python:3.9-slim
WORKDIR /app
COPY --from=python-bot /app /app
COPY --from=node-bot /app /app

# Environment variables (set up API tokens for deployment)
ENV API_TOKEN=your_telegram_api_token_here
EXPOSE 8000

# Run the bot manager script
CMD ["python", "bot_manager.py"]
