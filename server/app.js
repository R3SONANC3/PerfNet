import express from 'express';
import dashboardRoute from './routes/dashboardRoute.js';
import aiRoute from './routes/aiRoute.js';


const app = express();

app.use(express.json());

// Use the basic routes
app.use('/dashboardRoute', dashboardRoute);
app.use('/aiRoute', aiRoute);

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handling middleware for undefined routes
app.use((req, res) => {
    res.status(404).json({ error: 'Route not found' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});