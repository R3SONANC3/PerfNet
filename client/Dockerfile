# ใช้ Node.js image สำหรับ frontend
FROM node:18 as build

# สร้าง working directory
WORKDIR /app

# คัดลอก package.json และติดตั้ง dependencies
COPY package.json ./
RUN npm install

# คัดลอกไฟล์ทั้งหมดไปยัง container และ build
COPY . .
RUN npm run build

# ใช้ Nginx เป็น server สำหรับ static files
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# เปิด port สำหรับ frontend
EXPOSE 4173

# รัน Nginx
CMD ["nginx", "-g", "daemon off;"]
