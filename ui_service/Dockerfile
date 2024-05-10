# Используем образ с Node.js для сборки приложения
FROM node:14-alpine AS build

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копирование файлов package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей
RUN npm install

# Копирование остальных файлов приложения
COPY . .

# Сборка приложения
RUN npm run build

# Используем легковесный образ Nginx для запуска приложения
FROM nginx:alpine

# Копирование статических файлов из предыдущего этапа сборки
COPY --from=0 /app/build /usr/share/nginx/html

# Прослушивание порта 80
EXPOSE 80

# Команда для запуска Nginx
CMD ["nginx", "-g", "daemon off;"]
