FROM node:18-alpine AS builder

WORKDIR /app

# Copy package config and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build

# Use Nginx to serve the built static files
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port (Internal Nginx port)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
