# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Копіювання package files
COPY package*.json ./

# Встановлення залежностей
RUN npm install

# Копіювання вихідного коду
COPY . .

# Відкриття порту
EXPOSE 3000

# Запуск додатку
CMD ["npm", "start"]
