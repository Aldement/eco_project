from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os, random
from dotenv import load_dotenv
from model import get_trash
from Lists import facts, habits, quiz_questions


load_dotenv()
MODEL_PATH = os.getenv('MODEL_PATH')
LABELS_PATH = os.getenv('LABELS_PATH')


app = Flask(__name__)

app.secret_key = '097b918y31b2iu'

# Настройка директории для сохранения загруженных файлов
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Настройка базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'feedback.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель для хранения обратной связи
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Создание базы данных
with app.app_context():
    db.create_all()

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
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename).strip()
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            trash_class, confidence_procent = get_trash(filepath, MODEL_PATH, LABELS_PATH)
            print(f'Мне кажется, что с вероятностью {confidence_procent}% на фото {trash_class}')
            return render_template('result.html', trash_class=trash_class, filename=filename)
    return render_template('upload.html')

@app.route('/facts')
def facts_page():
    fact = random.choice(facts)
    habit = random.choice(habits)
    return render_template('facts.html', fact=fact, habit=habit)

@app.route('/refresh_facts')
def refresh_facts():
    return redirect(url_for('facts_page'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        user_answers = request.form
        score = 0
        for i, question in enumerate(quiz_questions):
            if user_answers.get(f'question-{i}') == question['answer']:
                score += 1
        
        session['score'] = score
        return redirect(url_for('quiz_result'))

    quiz_data = [{"index": i, "question": q["question"], "options": q["options"]} for i, q in enumerate(quiz_questions)]
    return render_template('quiz.html', quiz_questions=quiz_data)


@app.route('/quiz_result')
def quiz_result():
    score = session.get('score', 0)
    return render_template('quiz_result.html', score=score, total=len(quiz_questions))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Создание записи обратной связи
        new_feedback = Feedback(name=name, email=email, message=message)
        db.session.add(new_feedback)
        db.session.commit()

        flash('Спасибо за ваш отзыв!', 'success')
        return redirect(url_for('feedback'))

    return render_template('feedback.html')

@app.route('/feedbacks')
def feedbacks():
    all_feedbacks = Feedback.query.all()
    return render_template('feedbacks.html', feedbacks=all_feedbacks)


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
