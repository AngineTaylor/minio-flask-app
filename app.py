from flask import Flask, render_template, request, redirect, url_for, send_file
import boto3
from botocore.client import Config

app = Flask(__name__)
BUCKET = "my-files-bucket"

s3 = boto3.client(
    's3',
    endpoint_url='https://2b63-156-146-34-246.ngrok-free.app/',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    config=Config(signature_version='s3v4'),
)

@app.route('/')
def index():
    try:
        files = s3.list_objects(Bucket=BUCKET).get('Contents', [])
    except Exception as e:
        files = []
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    s3.upload_fileobj(file, BUCKET, file.filename)
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    file_path = f"/tmp/{filename}"
    s3.download_file(BUCKET, filename, file_path)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)