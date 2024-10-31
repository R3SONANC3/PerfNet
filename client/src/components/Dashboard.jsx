import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import { LineChart } from "@mui/x-charts/LineChart";
import axios from "axios";
import Papa from "papaparse";
import "../style.css";

const INTERVAL = 5000;
const MAX_DATA_POINTS = 5;

const queries = {
  cpu: '100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
  disk: '100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100) / node_filesystem_size_bytes{mountpoint="/"})',
  memory:
    "100 * (1 - ((node_memory_MemFree_bytes + node_memory_Cached_bytes + node_memory_Buffers_bytes) / node_memory_MemTotal_bytes))",
};

const theme = createTheme({
  palette: {
    mode: "dark",
  },
});

const MetricChart = ({ data, metric, label, color, unit }) => {
  const maxTicks = 5;

  const filteredData = data.filter(
    (d) => d[metric.toLowerCase()] !== null && !isNaN(d[metric.toLowerCase()])
  );

  const tickValues =
    filteredData.length > maxTicks
      ? filteredData
        .filter(
          (_, index) =>
            index % Math.ceil(filteredData.length / maxTicks) === 0
        )
        .map((d) => new Date(d.timestamp * 1000))
      : filteredData.map((d) => new Date(d.timestamp * 1000));

  return (
    <Paper
      elevation={3}
      sx={{ p: 2, display: "flex", flexDirection: "column", height: 240 }}
    >
      <Typography component="h2" variant="h6" color="primary" gutterBottom>
        {label} Usage
      </Typography>
      <LineChart
        xAxis={[
          {
            data: filteredData.map((d) => new Date(d.timestamp * 1000)),
            scaleType: "time",
            tickValues: tickValues,
            tickFormat: (value) => new Date(value).toLocaleTimeString(),
          },
        ]}
        series={[
          {
            data: filteredData.map((d) => parseFloat(d[metric.toLowerCase()])),
            label: `${label} ${unit}`,
            area: true,
            color: color,
          },
        ]}
        height={200}
        showLegend={true}
        legend={{ position: "bottom" }}
      />
    </Paper>
  );
};

function Dashboard() {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const prometheusUrl = queryParams.get("url");

  const [data, setData] = useState([]);
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [analyzedData, setAnalyzedData] = useState([]);
  const [notFoundErrors, setNotFoundErrors] = useState([]);
  const [systemMetrics, setSystemMetrics] = useState({});

  useEffect(() => {
    if (prometheusUrl) {
      console.log("Using PROMETHEUS_URL:", prometheusUrl);
    }
  }, [prometheusUrl]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const end = Math.floor(Date.now() / 1000);
        const start = end - MAX_DATA_POINTS * (INTERVAL / 1000);
        const step = INTERVAL / 1000;

        const results = await Promise.all(
          Object.entries(queries).map(async ([key, query]) => {
            const response = await axios.get(
              `${prometheusUrl}/api/v1/query_range`,
              {
                params: { query, start, end, step },
              }
            );
            if (
              response.data.status !== "success" ||
              !response.data.data.result.length
            ) {
              throw new Error(`No data returned for ${key}`);
            }
            return {
              key,
              values: response.data.data.result[0]?.values || [],
            };
          })
        );

        const newData = results[0].values.map((_, index) => {
          const point = { timestamp: results[0].values[index][0] };
          results.forEach(({ key, values }) => {
            const value = values[index] ? Number(values[index][1]) : NaN;
            point[key] = isNaN(value) ? null : value.toFixed(2); // Handle NaN
          });
          return point;
        });

        setData(newData);
        setError(null);
      } catch (error) {
        console.error("Error fetching data:", error);
        setError(
          "Failed to fetch data. Please check your Prometheus server connection."
        );
      }
    };

    if (prometheusUrl) {
      fetchData(); // Initial fetch
      const interval = setInterval(fetchData, INTERVAL);

      return () => clearInterval(interval);
    }
  }, [prometheusUrl]);

  const handleFileUpload = (event) => {
    setFile(event.target.files[0]);
    setError(null);
    setSuccess(null);
    setAnalysisResults(null);
  };

  const processCSV = () => {
    if (!file) {
      setError("Please upload a CSV file.");
      return;
    }

    setLoading(true);

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async (result) => {
        setLoading(false);
        const data = result.data;

        if (data.length === 0) {
          setError("CSV file is empty or invalid.");
          return;
        }

        const processedData = processData(data);

        if (processedData) {
          const averages = calculateAverages(processedData);
          setAnalysisResults(averages);
          setAnalyzedData(processedData);
          await sendToAPI(averages);
        }
      },
      error: (error) => {
        console.error("Error parsing CSV:", error);
        setError("Error parsing CSV file.");
        setLoading(false);
      },
    });
  };

  const processData = (data) => {
    try {
      const processedData = data.map((row) => {
        return {
          time_stamp: row.timeStamp || "N/A", // Include timestamp
          response_time: parseFloat(row.elapsed) || null, // Store in milliseconds
          response_code: row.responseCode || "N/A",
          success: row.success === "TRUE", // Convert to boolean
          failure_message: row.failureMessage || "N/A",
          url: row.URL || "N/A",
          latency: parseFloat(row.Latency) || null, // Store in milliseconds
          connect: parseFloat(row.Connect) || null, // Store in milliseconds
        };
      });

      const errors404 = processedData.filter(
        (row) => row.response_code === "404"
      );

      setNotFoundErrors(errors404);

      return processedData;
    } catch (error) {
      console.error("Error processing data:", error);
      setError("Error processing data.");
      return null;
    }
  };

  const getSystemMetricsAtTimestamp = async (timestamp) => {
    try {
      const formattedTimestamp = new Date(timestamp).toISOString();
      const prometheusUrl = "http://34.143.248.148:9090/api/v1/query";

      const queries = {
        cpu: 'rate(node_cpu_seconds_total[5m]) * 100',
        memory: 'node_memory_MemAvailable_bytes',
        disk: 'node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100',
      };

      const results = {};

      const cpuResponse = await axios.get(prometheusUrl, {
        params: {
          query: queries.cpu,
          time: formattedTimestamp,
        },
      });
      results.cpu = cpuResponse.data.data.result.length
        ? cpuResponse.data.data.result[0].value[1]
        : "N/A";

        console.log('cpuResponse:', JSON.stringify(cpuResponse.data, null, 2));

      const memoryResponse = await axios.get(prometheusUrl, {
        params: {
          query: queries.memory,
          time: formattedTimestamp,
        },
      });
      results.memory = memoryResponse.data.data.result.length
        ? memoryResponse.data.data.result[0].value[1]
        : "N/A";

      const diskResponse = await axios.get(prometheusUrl, {
        params: {
          query: queries.disk,
          time: formattedTimestamp,
        },
      });
      results.disk = diskResponse.data.data.result.length
        ? diskResponse.data.data.result[0].value[1]
        : "N/A";

      return results;
    } catch (error) {
      console.error("Error querying Prometheus:", error.message);
      return { error: error.message };
    }
  };

  const handleFetchMetrics = async (timestamp) => {
    const metrics = await getSystemMetricsAtTimestamp(timestamp);
    console.log(metrics);
    setSystemMetrics({ ...systemMetrics, [timestamp]: metrics });
  };

  const calculateMode = (arr) => {
    return arr
      .sort(
        (a, b) =>
          arr.filter((v) => v === a).length - arr.filter((v) => v === b).length
      )
      .pop();
  };

  const calculateAverages = (data) => {
    const validData = data.filter((item) => item.response_time !== null);

    const avg = (field) =>
      validData.reduce((sum, item) => sum + (item[field] || 0), 0) / validData.length;

    const avgTimeStamp = validData.length
      ? new Date(avg("time_stamp")).toLocaleString()
      : "No valid timestamps";

    const modeResponseCode = calculateMode(
      validData.map((item) => item.response_code).filter((code) => code !== "N/A")
    );

    return {
      avg_time_stamp: avgTimeStamp,
      avg_response_time: avg("response_time") || 0,
      mode_response_code: modeResponseCode || "N/A",
      avg_latency: avg("latency") || 0,
      avg_connect: avg("connect") || 0,
      total_success: validData.filter((item) => item.success).length,
      total_failure: validData.filter((item) => !item.success).length,
    };
  };

  const sendToAPI = async (averages) => {
    try {
      const response = await axios.post(
        "http://34.143.248.148:5000/analyze_performance",
        averages
      );
      setSuccess("Data successfully sent to API");
    } catch (error) {
      console.error("Error sending data to API:", error);
      setError("Failed to send data to API.");
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          minHeight: "100vh",
          bgcolor: "background.default",
          color: "text.primary",
        }}
      >
        <div className="dashboard-container">
          <div className="section graph">
            <div className="section-header">GRAPH</div>
            <div className="section-content">
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <MetricChart
                    data={data}
                    metric="CPU"
                    label="CPU"
                    color="#8884d8"
                    unit="(%)"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <MetricChart
                    data={data}
                    metric="Disk"
                    label="Disk"
                    color="#82ca9d"
                    unit="(%)"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <MetricChart
                    data={data}
                    metric="Memory"
                    label="Memory"
                    color="#ffc658"
                    unit="(%)"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Paper
                    elevation={3}
                    sx={{
                      p: 2,
                      display: "flex",
                      flexDirection: "column",
                      height: 240,
                      justifyContent: "center",
                      alignItems: "center",
                    }}
                  >
                    <Typography variant="h6" gutterBottom>
                      Upload CSV & Analyze
                    </Typography>
                    <input
                      accept=".csv"
                      id="contained-button-file"
                      type="file"
                      onChange={handleFileUpload}
                      style={{ display: "none" }}
                    />
                    <label htmlFor="contained-button-file">
                      <Button
                        variant="contained"
                        component="span"
                        sx={{ mb: 2 }}
                      >
                        Choose File
                      </Button>
                    </label>
                    {file && (
                      <Typography variant="body2" color="textSecondary">
                        Selected file: {file.name}
                      </Typography>
                    )}
                    <Button
                      onClick={processCSV}
                      disabled={loading || !file}
                      sx={{ mt: 2 }}
                    >
                      {loading ? "Processing..." : "Analyze"}
                    </Button>
                    {error && (
                      <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                        {error}
                      </Typography>
                    )}
                    {success && (
                      <Typography
                        variant="body2"
                        color="success"
                        sx={{ mt: 1 }}
                      >
                        {success}
                      </Typography>
                    )}
                  </Paper>
                </Grid>
              </Grid>
            </div>
          </div>
          <div className="bottom-section">
            <div className="section log">
              <div className="section-header">LOG</div>
              <div className="section-content">
                {notFoundErrors.length > 0 ? (
                  <Paper elevation={3} sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      404 Errors List
                    </Typography>
                    <ul>
                      {notFoundErrors.map((error, index) => (
                        <li key={index}>
                          TimeStamp: {error.time_stamp} - URL: {error.url} - Response Code: {error.response_code} - Failure Message: {error.failure_message}
                          <Button
                            onClick={() => handleFetchMetrics(error.time_stamp)}
                            sx={{ ml: 2 }}
                          >
                            Fetch Metrics
                          </Button>
                          {systemMetrics[error.time_stamp] && (
                            <div>
                              <Typography>CPU Usage: {systemMetrics[error.time_stamp].cpu}%</Typography>
                              <Typography>Memory Available: {systemMetrics[error.time_stamp].memory} bytes</Typography>
                              <Typography>Disk Usage: {systemMetrics[error.time_stamp].disk}%</Typography>
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </Paper>
                ) : (
                  <Typography>No 404 errors found.</Typography>
                )}
              </div>
            </div>
            <div className="section ai-results">
              <div className="section-header">RESULTS FROM AI</div>
              <div className="section-content">
                {analysisResults && (
                  <Paper elevation={3} sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      Analysis Results
                    </Typography>
                    <Typography>
                      Average Timestamp: {analysisResults.avg_time_stamp}
                    </Typography>
                    <Typography>
                      Average Response Time:{" "}
                      {analysisResults.avg_response_time.toFixed(2)} ms
                    </Typography>
                    <Typography>
                      Most Common Response Code:{" "}
                      {analysisResults.mode_response_code}
                    </Typography>
                    <Typography>
                      Average Latency: {analysisResults.avg_latency.toFixed(2)}{" "}
                      ms
                    </Typography>
                    <Typography>
                      Average Connect Time:{" "}
                      {analysisResults.avg_connect.toFixed(2)} ms
                    </Typography>
                    <Typography>
                      Total Successful Requests: {analysisResults.total_success}
                    </Typography>
                    <Typography>
                      Total Failed Requests: {analysisResults.total_failure}
                    </Typography>
                  </Paper>
                )}
              </div>
            </div>
          </div>
        </div>
      </Box>
    </ThemeProvider>
  );
}

export default Dashboard;