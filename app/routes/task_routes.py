from flask import Blueprint, abort, make_response, request
from sqlalchemy import desc
from app.models.task import Task
from app.routes.route_utilities import validate_model, create_model
import datetime
from ..db import db
import os
import requests

bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")


# Retrieve a model instance by its ID.
@bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)
    return task.to_dict()


# Get all tasks
@bp.get("")
def get_all_tasks():
    sort_order = request.args.get("sort")

    if sort_order is None:
        query = db.select(Task)
        tasks = db.session.scalars(query).all()

    # Sorts task by ascending order
    elif sort_order == "asc":
        asc_query = db.select(Task).order_by(Task.title)
        tasks = db.session.scalars(asc_query).all()

    # Sorts task by descending order
    elif sort_order == "desc":
        desc_query = db.select(Task).order_by(desc(Task.title))
        tasks = db.session.scalars(desc_query).all()

    else:
        response = "Invalid sort parameter"
        abort(make_response(response , 400))

    return [task.to_dict() for task in tasks]


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


# Update completion status on a task
@bp.patch("/<task_id>/mark_complete")
def task_completed(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = datetime.datetime.now()
    
    db.session.commit()    

    headers = {
        "Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"
    }
    requests.post(
        "https://slack.com/api/chat.postMessage",
        headers=headers,
        json={
            "channel": "task_list_api_test",
            "text": f"Someone just completed the task {task.title}"
        }
    )

    response =  make_response("", 204)
    response.mimetype = "application/json"

    return response


@bp.patch("/<task_id>/mark_incomplete")
def task_incomplete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = None

    db.session.commit()

    response =  make_response("", 204)
    response.mimetype = "application/json"
    
    return response