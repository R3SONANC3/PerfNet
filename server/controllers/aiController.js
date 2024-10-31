import express from 'express';
import axios from 'axios';

const app = express();
app.use(express.json());

// Route to call Python API
app.post('/analyze', async (req, res) => {
    try {
        const response = await axios.post('http://localhost:5000/analyze_performance', req.body);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: 'Error calling Python API' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});