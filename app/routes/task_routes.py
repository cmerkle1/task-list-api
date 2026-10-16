from flask import Blueprint, abort, make_response, request
from app.models.task import Task
from ..db import db

bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

# Validate model ID
def validate_model(cls, task_id):
    try:
        task_id = int(task_id)
    except:
        response = {"message": f"{cls.__name__} {task_id} invalid"}
        abort(make_response(response , 400))

    query = db.select(cls).where(cls.id == task_id)
    model = db.session.scalar(query)
    
    if not model:
        response = {"message": f"{cls.__name__} {task_id} not found"}
        abort(make_response(response, 404))
    
    return model


# Retrieve a model instance by its ID.
@bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)
    return task.to_dict()


# Get all tasks
@bp.get("")
def get_all_tasks():
    query = db.select(Task)
    tasks = db.session.scalars(query).all()
    return [task.to_dict() for task in tasks]


# Create new model
def create_model(cls, model_data):
    try:
        new_model = cls.from_dict(model_data)
        
    except KeyError:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))
    
    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201


# Handle the creation of new instances of a model from a dictionary, returning the expected responses.
@bp.post("")
def create_new_task():
    request_body = request.get_json()
    return create_model(Task, request_body)


# Update existing task
@bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    task_json = request.get_json()

    task.title = task_json["title"]
    task.description = task_json["description"]

    db.session.commit()    

    return make_response("", 204)


# Delete a task
@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return make_response("", 204)