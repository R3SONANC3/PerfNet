// // Define a route that uses the Hello controller function
// router.post('/analyze', async (req, res) => {
//     try {
//         const { time_stamp, response_time, response_code, success, failure_message, url, latency, connect } = req.body;

//         const pythonApiUrl = 'http://127.0.0.1:5000/analyze_performance'; 
//         const response = await axios.post(pythonApiUrl, {
//             time_stamp,
//             response_time,
//             response_code,
//             success,
//             failure_message,
//             url,
//             latency,
//             connect
//         }, {
//             headers: {
//                 'Content-Type': 'application/json'
//             }
//         });

//         res.json(response.data);
//     } catch (error) {
//         console.error('Error communicating with Python API:', error.message);
//         res.status(500).json({ error: 'Error communicating with Python API' });
//     }
// });
