from flask import Flask, render_template, request, redirect, url_for, send_file
import boto3
from botocore.client import Config
import os

app = Flask(__name__)
BUCKET = os.getenv("BUCKET", "my-files-bucket")


s3 = boto3.client(
    's3',
    endpoint_url=os.getenv("S3_ENDPOINT", "http://localhost:9000"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin"),
    config=Config(signature_version='s3v4', s3={'addressing_style': 'path'})
)

@app.route('/')
def index():
    try:
        files = s3.list_objects(Bucket=BUCKET).get('Contents', [])
        print(f"✅ Файлы в бакете {BUCKET}: {[f['Key'] for f in files]}")
    except Exception as e:
        print(f"❌ Ошибка получения файлов: {e}")
        files = []
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        print("❌ Нет файла в запросе")
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        print("❌ Пустое имя файла")
        return redirect(url_for('index'))

    try:
        s3.upload_fileobj(file, BUCKET, file.filename)
        print(f"✅ Файл '{file.filename}' успешно загружен")
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    file_path = f"/tmp/{filename}"
    try:
        s3.download_file(BUCKET, filename, file_path)
        print(f"✅ Файл '{filename}' скачан")
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")
        return redirect(url_for('index'))
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)