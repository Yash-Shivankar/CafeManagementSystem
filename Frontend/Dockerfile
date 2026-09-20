# syntax=docker/dockerfile:1
#
# Build context is the REPO ROOT, not Frontend/ — the image serves both the
# React app and the landing page, and landing/ sits beside Frontend/.
#   docker build -f Frontend/Dockerfile .

FROM node:22-alpine AS build

WORKDIR /app

COPY Frontend/package.json Frontend/package-lock.json ./
RUN npm ci

COPY Frontend/ ./

ARG VITE_BACKEND_URL=""
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL

RUN npm run build

FROM nginx:1.27-alpine AS runtime

COPY --from=build /app/dist /usr/share/nginx/html/app
COPY landing/ /usr/share/nginx/html/landing/
COPY Frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1
