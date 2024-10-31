import React, { useState } from 'react';
import Papa from 'papaparse';
import axios from 'axios';

const PerformanceAnalyzer = () => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile && uploadedFile.type !== 'text/csv') {
      setError('Please upload a valid CSV file.');
      setFile(null);
      return;
    }
    setFile(uploadedFile);
    setError(null);
    setSuccess(null);
  };

  const processCSV = () => {
    if (!file) {
      setError('Please upload a CSV file.');
      return;
    }

    setLoading(true);

    try {
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: async (result) => {
          setLoading(false);
          const data = result.data;

          if (data.length === 0) {
            setError('CSV file is empty or invalid.');
            return;
          }

          const processedData = processData(data);

          if (processedData) {
            console.log("Processed Data:", processedData);
            const averages = calculateAverages(processedData);
            console.log("Averages:", averages);
            await sendToAPI(averages);
          }
        },
        error: (error) => {
          console.error('Error parsing CSV:', error);
          setError('Error parsing CSV file.');
          setLoading(false);
        },
      });
    } catch (error) {
      setLoading(false);
      console.error('Unexpected error during CSV processing:', error);
      setError('Unexpected error during CSV processing.');
    }
  };

  const processData = (data) => {
    try {
      return data.slice(0, 100).map((row) => ({
        time_stamp: parseInt(row.timeStamp),
        response_time: parseFloat(row.elapsed),
        response_code: row.responseCode,
        success: row.success === 'TRUE',
        failure_message: row.failureMessage || 'N/A',
        url: row.URL,
        latency: parseFloat(row.Latency),
        connect: parseFloat(row.Connect),
      }));
    } catch (error) {
      console.error('Error processing data:', error);
      setError('Error processing data.');
      return null;
    }
  };

  const calculateMode = (arr) => {
    return arr.sort((a, b) =>
      arr.filter(v => v === a).length - arr.filter(v => v === b).length
    ).pop();
  };

  const calculateAverages = (data) => {
    const avg = (field) =>
      data.reduce((sum, item) => sum + (item[field] || 0), 0) / data.length;

    const avgTimeStamp = new Date(avg('time_stamp')).toLocaleString();
    const modeResponseCode = calculateMode(data.map(item => item.response_code));

    return {
      avg_time_stamp: avgTimeStamp,
      avg_response_time: avg('response_time'),
      mode_response_code: modeResponseCode,
      avg_latency: avg('latency'),
      avg_connect: avg('connect'),
      total_success: data.filter((item) => item.success).length,
      total_failure: data.filter((item) => !item.success).length,
    };
  };

  const sendToAPI = async (averages) => {
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/analyze_performance`, averages);
      setSuccess('Data successfully sent to API');
    } catch (error) {
      console.error('Error sending data to API:', error.response?.data || error.message);
      setError('Failed to send data to API.');
    }
  };

  const getSystemMetricsAtTimestamp = async (timestamp) => {
    try {
      if (!timestamp) {
        throw new Error('Invalid request: timestamp is required.');
      }

      const formattedTimestamp = new Date(timestamp).toISOString();
      const prometheusUrl = 'http://34.143.248.148:9090/api/v1/query';

      const queries = {
        cpu: 'query?query=100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
        memory: 'query?query=100 * (1 - ((node_memory_MemFree_bytes + node_memory_Cached_bytes + node_memory_Buffers_bytes) / node_memory_MemTotal_bytes))',
        disk: 'query?query=100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100) / node_filesystem_size_bytes{mountpoint="/"})',
      };

      const results = {};

      const cpuResponse = await axios.get(prometheusUrl, {
        params: {
          query: queries.cpu,
          time: formattedTimestamp,
        },
      });
      results.cpu = cpuResponse.data?.data?.result;

      const memoryResponse = await axios.get(prometheusUrl, {
        params: {
          query: queries.memory,
          time: formattedTimestamp,
        },
      });
      results.memory = memoryResponse.data?.data?.result;

      const diskResponse = await axios.get(prometheusUrl, {
        params: {
          query: queries.disk,
          time: formattedTimestamp,
        },
      });
      results.disk = diskResponse.data?.data?.result;

      return results;
    } catch (error) {
      console.error('Error fetching system metrics:', error);
      throw error;
    }
  };

  return (
    <div>
      <h1>Performance Analyzer</h1>
      <input type="file" onChange={handleFileUpload} accept=".csv" />
      {file && <p>File selected: {file.name}</p>}
      <button onClick={processCSV} disabled={loading}>
        {loading ? 'Processing...' : 'Analyze CSV'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {success && <p style={{ color: 'green' }}>{success}</p>}
    </div>
  );
};

export default PerformanceAnalyzer;