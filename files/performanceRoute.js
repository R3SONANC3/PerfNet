// import express from 'express';
// import fs from 'fs';
// import path from 'path';
// import * as tf from '@tensorflow/tfjs'; 
// import Performance from '../models/performanceModel.js';
// import { trainAIModel, predictPerformance } from '../ai/aiModel.js';

// const router = express.Router();

// // Load model
// const modelPath = path.join(process.cwd(), 'ai', 'model.json'); 

// // Check model
// const loadModel = async () => {
//     try {
//         if (fs.existsSync(modelPath)) {
//             const model = await tf.loadLayersModel(`file://${modelPath}`);
//             console.log('Model loaded successfully.');
//             return model;
//         } else {
//             console.log('No model found to load.');
//             return null;
//         }
//     } catch (error) {
//         console.error('Error loading model:', error.message);
//         return null;
//     }
// };


// // Save model
// const saveModel = async (model) => {
//     try {
//         await model.save(`file://${modelPath}`);
//         console.log('Model saved successfully.');
//     } catch (error) {
//         console.error('Error saving model:', error.message);
//     }
// };

// // Route to collect performance data
// router.post('/collect', async (req, res) => {
//     try {
//         const { cpuUsage, memoryUsage, responseTime } = req.body;
//         const newPerformance = new Performance({ cpuUsage, memoryUsage, responseTime });
        
//         await newPerformance.save();
//         res.status(201).json({ message: 'Data collected successfully' });

//         const data = await Performance.find();
//         const model = await trainAIModel(data); // Train the model
//         req.app.locals.model = model; // Store model in app locals
        
//         // Save the trained model
//         await saveModel(model); // Use the new saveModel function
        
//     } catch (error) {
//         if (!res.headersSent) { 
//             res.status(500).json({ error: error.message });
//         }
//     }
// });

// // Route to get all performance data
// router.get('/', async (req, res) => {
//     try {
//         const data = await Performance.find();
//         res.status(200).json(data);
//     } catch (error) {
//         res.status(500).json({ error: error.message });
//     }
// });

// // Route to get performance prediction
// router.post('/predict', async (req, res) => {
//     try {
//         const { cpuUsage, memoryUsage } = req.body;
//         let model = req.app.locals.model; // Get the AI model from app locals
        
//         if (!model) {
//             model = await loadModel();
//         }

//         if (!model) {
//             return res.status(500).json({ error: 'AI model not trained' });
//         }

//         const prediction = await predictPerformance(model, [cpuUsage, memoryUsage]);
//         res.status(200).json({ prediction });
//     } catch (error) {
//         res.status(500).json({ error: error.message });
//     }
// });

// export default router;
