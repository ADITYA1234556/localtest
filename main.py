import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)


# Database configuration
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://adi:admin@mysql-service:3306/admin'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('MYSQL_URI', 'mysql+pymysql://adi:admin@mysql-service:3306/admin') #user:password@database-service:port/databasename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    done = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Task({self.title}, {self.description}, {self.done})"

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def home():
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)

# CREATE task
@app.route('/tasks', methods=['GET','POST'])
def create_task():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        done = True if request.form.get("done") == "on" else False
        if not title:
            return render_template("task_form.html", error = "Title is required")
        new_task = Task(title=title, description=description, done=done)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("task_form.html")

# READ single task
@app.route('/tasks/<int:task_id>')
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template("task_list.html", task=task)

# UPDATE task
@app.route('/tasks/edit/<int:task_id>', methods=['GET','POST'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == "POST":
        task.title = request.form.get('title', task.title)
        task.description = request.form.get('description', task.description)
        task.done = bool(request.form.get('done', task.done))
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("task_form.html", task=task)


# DELETE task
@app.route('/tasks/<int:task_id>', methods=['POST','DELETE'])
def delete_task(task_id):
    appkey = request.args.get("appkey")
    if appkey == "websitesecret":
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template("error.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')