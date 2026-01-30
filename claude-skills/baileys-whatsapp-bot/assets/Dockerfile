# Use official Node image
FROM node:20-alpine
WORKDIR /app

# Install deps
COPY package.json tsconfig.json /app/
RUN npm install

# Copy source
COPY src /app/src

# Build
RUN npm run build

# Runtime env
ENV AUTH_DIR=/app/baileys_auth_info
ENV PORT=8080

EXPOSE 8080
CMD ["npm", "start"]
