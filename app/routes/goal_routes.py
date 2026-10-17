from flask import Blueprint, abort, make_response, request
from app.routes.task_routes import validate_model, create_model
from app.models.goal import Goal
from ..db import db

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

# Retrieve a goal model instance by its ID.
@bp.get("/<goal_id>")
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    return goal.to_dict()


# Get all goals
@bp.get("")
def get_all_goals():
    query = db.select(Goal)
    goals = db.session.scalars(query).all()
    return [goal.to_dict() for goal in goals]

# Handle the creation of new instances of a model from a dictionary, returning the expected responses.
@bp.post("")
def create_new_goal():
    request_body = request.get_json()
    return create_model(Goal, request_body)


# Update existing goal
@bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    goal_json = request.get_json()

    goal.title = goal_json["title"]

    db.session.commit()    

    response = make_response("", 204)
    response.mimetype = "application/json"
    return response

# Delete a goal
@bp.delete("/<goal_id>")
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    db.session.delete(goal)
    db.session.commit()

    return make_response("", 204)
