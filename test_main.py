import pytest
from main import app, db, Task

# Use Flask's test client
@pytest.fixture
def client():
    # Set the app's testing configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory SQLite database for tests
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    # Set up the test database (creating tables)
    with app.app_context():
        db.create_all()

    # Create a test client to interact with the app
    with app.test_client() as client:
        yield client

    # Clean up the test database after tests
    with app.app_context():
        db.session.remove()
        db.drop_all()
# Test GET /tasks endpoint without hitting the real database
def test_get_tasks(client, mocker):
    # Add tasks to the in-memory database before the test
    task1 = Task(title="New Task 1", description="Description for task 1", done=False)
    task2 = Task(title="New Task 2", description="Description for task 2", done=True)
    db.session.add(task1)
    db.session.add(task2)
    db.session.commit()

    # Now perform the GET request
    response = client.get('/tasks')

    # Print the raw HTML content for debugging
    print(response.data.decode())  # Check what HTML is being returned

    # Check the response
    assert response.status_code == 200
    # Check if the tasks are returned in the response (ensure titles are in <h3> tags)
    assert b"<h3>New Task 1</h3>" in response.data
    assert b"<h3>New Task 2</h3>" in response.data

# Test POST /tasks (Create Task)
def test_create_task(client):
    task_data = {
        'title': 'New Task',
        'description': 'Description for new task'
    }
    response = client.post('/tasks', data=task_data)

    # Check the response
    assert response.status_code == 302  # Should redirect to home page
    new_task = Task.query.filter_by(title='New Task').first()
    assert new_task is not None
    assert new_task.description == 'Description for new task'

# Test POST /tasks/<task_id> (Update Task)
def test_update_task(client):
    # Add a task to the in-memory database before the test
    task = Task(title="Old Task", description="Old description", done=False)
    db.session.add(task)
    db.session.commit()

    updated_task_data = {
        'title': 'Updated Task',
        'description': 'Updated description',
        'done': True
    }

    # Perform the POST request to update the task
    response = client.post(f'/tasks/edit/{task.id}', data=updated_task_data)

    # Check the response
    assert response.status_code == 302  # Should redirect to home page after update
    updated_task = Task.query.get(task.id)
    assert updated_task.title == 'Updated Task'
    assert updated_task.description == 'Updated description'
    assert updated_task.done is True

# Test POST /tasks/<task_id> (Delete Task)
def test_delete_task(client):
    # Add a task to the in-memory database before the test
    task = Task(title="Task to delete", description="This task will be deleted", done=False)
    db.session.add(task)
    db.session.commit()

    # Perform the POST request to delete the task
    response = client.post(f'/tasks/{task.id}', follow_redirects=True)

    # Check the response
    assert response.status_code == 200  # Should successfully render the home page
    # Verify the task was actually deleted from the database
    deleted_task = Task.query.get(task.id)
    assert deleted_task is None  # Task should no longer exist in the database
