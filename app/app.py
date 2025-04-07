from flask import Flask, request, jsonify, send_from_directory
import os
import json
from datetime import datetime
from flask_cors import CORS

from analysis import start_analysis

app = Flask(__name__, static_folder='static')
CORS(app) 

# Directory for storing submitted inquiries
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# Serve static files (HTML, CSS, JS)
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# API endpoint to handle rental inquiries
@app.route('/api/submit', methods=['POST'])
def submit_rental_inquiry():
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        required_fields = ['quarter', 'region', 'industry', 'budget_min', 'budget_max', 'talent']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        
        # Save inquiry to a file
        inquiry_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{data['region']}_{data['industry']}"
        file_path = os.path.join(DATA_DIR, f"{inquiry_id}.json")
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

        # Business logic to process the inquiry
        message = run_analysis(data)
        
        return jsonify({
            'success': True,
            'message': message,
            'inquiry_id': inquiry_id
        })
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500
    

def run_analysis(data):
    market_details = start_analysis(
        region=data['region'],
        industry=data['industry'],
        quarter=data['quarter'],
        low_budget=data['budget_min'],
        high_budget=data['budget_max'],
        talent=data['talent']
    )
    
    return market_details


if __name__ == '__main__':
    # Create a folder structure for static files
    static_dir = 'static'
    os.makedirs(static_dir, exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, port=5000)