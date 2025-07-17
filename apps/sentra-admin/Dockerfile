FROM node:20-alpine
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Expose Vite dev server port (matches docker-compose.dev.yml)
EXPOSE 3200
EXPOSE 9329

# Start Vite dev server with debugging enabled
# The --inspect flag allows for remote debugging on port 9229
CMD ["npm", "run", "dev"]
