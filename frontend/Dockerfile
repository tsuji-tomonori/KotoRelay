FROM node:22-bookworm-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/package.json
RUN npm ci --ignore-scripts
COPY frontend frontend
COPY tools/project/csp.mjs tools/project/csp.mjs
ENV ASTRO_TELEMETRY_DISABLED=1
RUN npm run build && node tools/project/csp.mjs
FROM nginxinc/nginx-unprivileged:1.28-alpine
COPY --from=build /app/artifacts/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/frontend/dist /usr/share/nginx/html
