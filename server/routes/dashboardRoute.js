import express from 'express';
import axios from 'axios'; // ใช้ axios สำหรับยิง API
import { Hello } from '../controllers/dashboardController.js';  

const router = express.Router();

// Define a route that uses the Hello controller function
router.get('/hello', Hello);

// Define a route that uses the Hello controller function
router.post('/getURL', async (req, res) => {
    try {
        const { url, time_stamp } = req.body; 

        if (!url || !time_stamp) {
            return res.status(400).json({ message: 'URL and time_stamp are required' });
        }

        // ยิง API ไปที่ URL ที่ได้รับมา
        const response = await axios.get(url);
        
        // สร้าง URL ใหม่โดยใช้ข้อมูลที่ได้รับจาก API ที่ยิงไปก่อนหน้านี้ พร้อมใส่ time_stamp ใน parameter
        const newUrl = `https://example.com/new-api-endpoint?param=${response.data.someParameter}&time_stamp=${time_stamp}`;

        // ยิง API ไปที่ URL ใหม่ที่สร้างขึ้น
        const newResponse = await axios.get(newUrl);

        // ตรวจสอบว่ามีข้อมูลใดตรงกับ time_stamp ที่ระบุหรือไม่
        const matchedData = newResponse.data.find(item => item.time_stamp === time_stamp);

        if (matchedData) {
            res.status(200).json({ message: 'Data found', data: matchedData });
        } else {
            res.status(404).json({ message: 'No data matched with the provided time_stamp' });
        }

    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Error while processing the URLs', error: error.message });
    }
});

export default router;