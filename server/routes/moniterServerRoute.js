import express from 'express';
import axios from 'axios'; 

const router = express.Router();

// Define a route that uses the Hello controller function
router.post('/getResource', async (req, res) => {
    try {
        const { timeStamp,url } = req.body
        url=('${url}/api/v1/query?query=100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)')
        const response = await axios.post(url, {
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        res.json(response.data);
    }catch (error) {
        console.error('Error communicating with Python API:', error.message);
        res.status(500).json({ error: 'Error communicating with Python API' });
    }
    
});

export default router;