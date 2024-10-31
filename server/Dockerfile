# ใช้ Node.js image สำหรับ backend
FROM node:18

# สร้าง working directory
WORKDIR /app

# คัดลอก package.json และติดตั้ง dependencies
COPY package.json ./
RUN npm install

# คัดลอกไฟล์ทั้งหมดไปยัง container
COPY . .

# เปิด port สำหรับ backend
EXPOSE 5000

# รัน server
CMD ["node", "server.js"]
