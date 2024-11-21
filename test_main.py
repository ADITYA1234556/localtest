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

    # Check the response
    assert response.status_code == 200
    # Check if the tasks are returned in the response (you may need to adapt this based on your HTML response)
    assert b"New Task 1" in response.data
    assert b"New Task 2" in response.data

# Test PUT /tasks/<task_id> endpoint (Update Task)
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

    # Perform the PUT request to update the task with ID 1
    response = client.post(f'/tasks/{task.id}', json=updated_task_data)

    # Check the response
    assert response.status_code == 200  # Redirect to home page after update
    updated_task = Task.query.get(task.id)
    assert updated_task.title == 'Updated Task'
    assert updated_task.description == 'Updated description'
    assert updated_task.done is True


# Test DELETE /tasks/<task_id> endpoint (Delete Task)
def test_delete_task(client):
    # Add a task to the in-memory database before the test
    task = Task(title="Task to delete", description="This task will be deleted", done=False)
    db.session.add(task)
    db.session.commit()

    # Perform the DELETE request to delete the task with ID 1
    response = client.delete(f'/tasks/{task.id}')

    # Check the response
    assert response.status_code == 200  # Should redirect to the home page
    # Verify the task was actually deleted from the database
    deleted_task = Task.query.get(task.id)
    assert deleted_task is None  # Task should no longer exist in the database

