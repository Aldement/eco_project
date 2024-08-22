from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os, random
from dotenv import load_dotenv
from model import get_trash


load_dotenv()
MODEL_PATH = os.getenv('MODEL_PATH')
LABELS_PATH = os.getenv('LABELS_PATH')


app = Flask(__name__)

facts = [
    "Пластиковые бутылки разлагаются около 500 лет.",
    "Потребление бумаги можно сократить, используя электронные документы.",
    "Зеленые крыши помогают уменьшить тепловой остров и экономить энергию.",
    "Переработка одного алюминиевого баночка экономит достаточно энергии для работы телевизора в течение трех часов."
]

habits = [
    "Используйте многоразовые сумки для покупок.",
    "Сортируйте мусор.",
    "Выключайте свет, когда он не нужен.",
    "Используйте энергосберегающие лампочки."
]

# Настройка директории для сохранения загруженных файлов
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/type_trash', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Проверка на наличие файла в запросе
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Здесь будет код для определения класса изображения
            predicted_class = "example_class"  # Здесь можно подключить модель для предсказания
            return render_template('result.html', predicted_class=predicted_class, filename=filename)
    return render_template('upload.html')

@app.route('/facts')
def facts_page():
    fact = random.choice(facts)
    habit = random.choice(habits)
    return render_template('facts.html', fact=fact, habit=habit)

@app.route('/refresh_facts')
def refresh_facts():
    return redirect(url_for('facts_page'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
