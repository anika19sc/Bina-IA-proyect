# Stage 1: Build the Angular application
FROM node:18 as build

WORKDIR /app

# Copy package files and install dependencies
# We assume the user will generate the project files here.
# If starting from scratch, we might need to handle the case where package.json doesn't exist yet.
# For now, we assume the standard Angular structure.

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build --prod

# Stage 2: Serve with Nginx
FROM nginx:alpine

COPY --from=build /app/dist/bina-legal/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
