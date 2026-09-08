# SecSim frontend — Vue 3 + Vite (multi-stage: build, then serve static).
# Pass the API origin at build time: --build-arg VITE_API_URL=http://host:5000/api
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL=http://localhost:5000/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Production stage: nginx serving dist/ with SPA fallback (see nginx.conf).
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
