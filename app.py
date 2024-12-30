# app.py

from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

# Route to serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/execute', methods=['POST'])
def execute():
    data = request.get_json()
    if not data or 'input_value' not in data:
        return jsonify({'status': 'fail', 'message': 'No input provided'}), 400
    
    input_value = data['input_value']
    
    try:
        # Ensure main.py is in the same directory as app.py
        script_path = os.path.join(os.path.dirname(__file__), 'main.py')
        
        # Execute main.py with the input_value as a parameter
        result = subprocess.run(
            ['python3', script_path, input_value],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Capture the output from main.py
        output = result.stdout.strip()
        
        return jsonify({'status': 'success', 'output': output}), 200
    except subprocess.CalledProcessError as e:
        # Handle errors in executing main.py
        error_msg = e.stderr.strip() if e.stderr else 'An error occurred.'
        return jsonify({'status': 'fail', 'message': error_msg}), 500
    except Exception as e:
        # Handle other exceptions
        return jsonify({'status': 'fail', 'message': str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app on localhost:5000
    app.run(debug=True)
