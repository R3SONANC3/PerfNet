// import express from 'express';
// import Performance from './models/performanceModel.js';
// import { trainAIModel, predictPerformance as aiPredictPerformance } from '../ai/aiModel.js';

// const router = express.Router();

// let aiModel = null;

// export const collectPerformanceData = async (req, res) => {
//     const { systemName, responseTime, cpuUsage, memoryUsage } = req.body;

//     try {
//         const performance = new Performance({
//             systemName,
//             responseTime,
//             cpuUsage,
//             memoryUsage,
//         });
//         await performance.save();

//         const data = await Performance.find().lean();
//         aiModel = await trainAIModel(data);

//         res.status(201).json({ message: 'Data collected successfully' });
//     } catch (error) {
//         res.status(500).json({ error: error.message });
//     }
// };

// export const predictPerformance = async (req, res) => {
//     const { cpuUsage, memoryUsage } = req.body;

//     if (!aiModel) {
//         return res.status(400).json({ error: 'AI model is not trained yet' });
//     }

//     try {
//         const prediction = await aiPredictPerformance(aiModel, [cpuUsage, memoryUsage]);
//         res.json({ predictedResponseTime: prediction });
//     } catch (error) {
//         res.status(500).json({ error: error.message });
//     }
// };

// export default router;
