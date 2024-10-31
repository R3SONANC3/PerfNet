from flask import Flask, request, jsonify
import openai
import pandas as pd

app = Flask(__name__)

# Set OpenAI API key
# Define a route to analyze performance data
@app.route('/analyze_performance', methods=['POST'])
def analyze_performance():
    data = request.json
    time_stamp = data.get('time_stamp')
    response_time = data.get('response_time')
    response_code = data.get('response_code')
    success = data.get('success')
    failure_message = data.get('failure_message', 'N/A')
    url = data.get('url')
    latency = data.get('latency')
    connect = data.get('connect')

    analysis_result = check_performance_with_openai(time_stamp, response_time, response_code, success, failure_message, url, latency, connect)
    
    return jsonify({"analysis_result": analysis_result})

# Function to check performance
def check_performance_with_openai(time_stamp, response_time, response_code, success, failure_message, url, latency, connect):
    prompt = f"""
    You are a performance testing expert. We have collected some performance test data and would like your analysis.
    
    Here are the specific details:
    - TimeStamp: {time_stamp}
    - Response Time (Elapsed): {response_time} ms
    - Response Code: {response_code}
    - Success: {success}
    - Failure Message: {failure_message}
    - URL: {url}
    - Latency: {latency} ms
    - Connect: {connect} ms
    
    Based on this data, is the response time:
    - Good 
    - About to be problematic
    - Not good
    
    if it Good Respond juct Good
    
    Respond with only one of the above options.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in performance testing."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

if __name__ == '__main__':
    app.run(port=5000, debug=True)