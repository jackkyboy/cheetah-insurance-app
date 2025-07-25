# Stage 1: Build React
FROM node:18-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY public ./public
COPY src ./src
RUN npm run build

# Stage 2: Serve with NGINX
FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
