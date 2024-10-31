// import express from 'express';
// import cors from 'cors';
// import sequelize from './config/db.js'; // ใช้ .js
// import User from './models/User.js'; // ใช้ .js

// const app = express();

// app.use(cors());
// app.use(express.json());

// // สร้างตาราง User
// sequelize.sync();

// // API สำหรับบันทึกข้อมูล
// app.post('/api/users', async (req, res) => {
//   try {
//     const { name, email } = req.body;
//     const user = await User.create({ name, email });
//     res.status(201).json(user);
//   } catch (err) {
//     res.status(500).json({ error: 'Failed to save user' });
//   }
// });

// // API สำหรับดึงข้อมูล
// app.get('/api/users', async (req, res) => {
//   try {
//     const users = await User.findAll();
//     res.status(200).json(users);
//   } catch (err) {
//     res.status(500).json({ error: 'Failed to fetch users' });
//   }
// });

// const port = 5000;
// app.listen(port, '0.0.0.0', () => {
//   console.log(`Backend running on http://0.0.0.0:${port}`);
// });

