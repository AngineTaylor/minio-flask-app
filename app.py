from flask import Flask, render_template, request, redirect, url_for, send_file
import boto3
from botocore.client import Config
import os
from flask_sqlalchemy import SQLAlchemy

# === Создаём приложение Flask ===
app = Flask(__name__)

# === Настройка базы данных (PostgreSQL или SQLite для локального запуска) ===
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///files.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# === Инициализируем SQLAlchemy ===
db = SQLAlchemy(app)

# === Модель базы данных ===
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<File {self.id}>"

# === Создание таблицы при первом запуске ===
with app.app_context():
    db.create_all()

# === Настройка клиента S3 (MinIO) ===
s3 = boto3.client(
    's3',
    endpoint_url=os.getenv("S3_ENDPOINT", "http://localhost:9000"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin"),
    config=Config(signature_version='s3v4', s3={'addressing_style': 'path'})
)

BUCKET = os.getenv("BUCKET", "my-files-bucket")

# === Главная страница ===
@app.route('/')
def index():
    try:
        files = s3.list_objects(Bucket=BUCKET).get('Contents', [])
    except Exception as e:
        print(f"Ошибка при получении файлов из MinIO: {e}")
        files = []

    db_files = File.query.all()
    return render_template('index.html', files=files, db_files=db_files)

# === Загрузка файла ===
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        print("❌ Ошибка: файл не найден в запросе")
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        print("❌ Ошибка: имя файла пустое")
        return redirect(url_for('index'))

    try:
        # Загружаем в MinIO
        s3.upload_fileobj(file, BUCKET, file.filename)

        # Сохраняем имя файла в БД
        new_file = File(filename=file.filename)
        db.session.add(new_file)
        db.session.commit()

        print(f"✅ Файл '{file.filename}' загружен и записан в БД")
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return redirect(url_for('index'))

    return redirect(url_for('index'))

# === Скачивание файла ===
@app.route('/download/<filename>')
def download(filename):
    file_path = f"/tmp/{filename}"
    try:
        s3.download_file(BUCKET, filename, file_path)
    except Exception as e:
        print(f"Ошибка скачивания: {e}")
        return redirect(url_for('index'))
    return send_file(file_path, as_attachment=True)

# === Точка входа ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))