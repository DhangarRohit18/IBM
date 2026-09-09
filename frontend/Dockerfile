# ─────────────────────────────────────────────────────────
# LEGACYX Frontend — Dockerfile (Development)
# ─────────────────────────────────────────────────────────
FROM node:20-alpine

WORKDIR /app

# Install dependencies first (layer caching)
COPY package.json package-lock.json* ./
RUN npm install

# Copy source
# In dev, this is overridden by a bind mount.
COPY . .

EXPOSE 5173

# Vite dev server with host exposed for Docker
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
