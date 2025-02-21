from flask import Flask, request, render_template, jsonify, send_file
import os
import qrcode
import uuid

# Import custom functions
from utils.transcriber import transcribe_audio
from utils.analyzer import analyze_keywords, analyze_emotion
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the file is an allowed format."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'audio' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['audio']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file format"}), 400

        file_id = str(uuid.uuid4())  # Unique ID for each file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.wav")
        file.save(file_path)

        # Process audio
        transcribed_text = transcribe_audio(file_path)
        keywords_found = analyze_keywords(transcribed_text)
        emotion_detected = analyze_emotion(file_path)

        scam_detected = bool(keywords_found) or (emotion_detected in ['fear', 'anger'])

        result = {
            'file_id': file_id,
            'transcription': transcribed_text,
            'keywords_found': keywords_found,
            'emotion_detected': emotion_detected,
            'scam_detected': scam_detected
        }

        # Save result to a file
        result_path = os.path.join("static", f"{file_id}.json")
        with open(result_path, "w") as f:
            f.write(str(result))

        # Generate QR Code for Mobile Access
        server_url = "https://fba8-103-203-173-18.ngrok-free.app"  # Change this to your ngrok URL
        scan_url = f"{server_url}/check_scam/{file_id}"
        qr = qrcode.make(scan_url)
        qr_path = os.path.join("static", f"{file_id}.jpg")
        qr.save(qr_path, format="JPEG")

        os.remove(file_path)  # Clean up uploaded file

        return render_template('index.html', qr_url=qr_path, scan_url=scan_url)

    return render_template('index.html')

@app.route('/check_scam/<file_id>')
def check_scam(file_id):
    """Show Scam Call Analysis on Mobile After Scanning QR Code."""
    result_path = os.path.join("static", f"{file_id}.json")
    
    if not os.path.exists(result_path):
        return "No scam data found for this QR code.", 404

    with open(result_path, "r") as f:
        data = eval(f.read())  # Read JSON-like string

    return render_template('result.html', result=data)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
