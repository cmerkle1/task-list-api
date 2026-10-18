from flask import abort, make_response
from ..db import db

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