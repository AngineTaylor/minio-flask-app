from flask import Flask, render_template, request, redirect, url_for, send_file
import boto3
from botocore.client import Config
import os

app = Flask(__name__)
BUCKET = "my-files-bucket"

# Используем переменные окружения для настройки S3 клиента
s3 = boto3.client(
    's3',
    endpoint_url='https://c7af-79-110-55-50.ngrok-free.app/ ',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    config=Config(signature_version='s3v4', s3={'addressing_style': 'path'})
)

@app.route('/')
def index():
    try:
        files = s3.list_objects(Bucket=BUCKET).get('Contents', [])
    except Exception as e:
        print(f"Error fetching files: {e}")
        files = []
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    try:
        s3.upload_fileobj(file, BUCKET, file.filename)
    except Exception as e:
        print(f"Upload error: {e}")
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    file_path = f"/tmp/{filename}"
    try:
        s3.download_file(BUCKET, filename, file_path)
    except Exception as e:
        print(f"Download error: {e}")
        return redirect(url_for('index'))
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)