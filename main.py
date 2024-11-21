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
        if not title:
            return render_template("task_form.html", error = "Title is required")
        new_task = Task(title=title, description=description)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("task_form.html")

# READ all tasks
@app.route('/tasks')
def get_tasks():
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)

# READ single task
@app.route('/tasks/<int:task_id>')
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template("task_list.html", task=task)

# UPDATE task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    task_data = request.get_json()  # Expecting JSON data

    task.title = task_data.get('title', task.title)
    task.description = task_data.get('description', task.description)
    task.done = task_data.get('done', task.done)

    db.session.commit()
    return jsonify({'message': 'Task updated successfully'}), 200


# DELETE task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
