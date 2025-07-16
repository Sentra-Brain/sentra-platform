FROM node:20-alpine
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Expose Vite dev server port (matches docker-compose.dev.yml)
EXPOSE 3001

# Start Vite dev server
CMD ["npm", "run", "dev", "--", "--port", "3001", "--host"]
