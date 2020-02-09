import models
from application import bcrypt

def authenticate(email, password):
    user = models.User.query.filter_by(email=email).first()
    if user:
        pw_hash = user.password
        if bcrypt.check_password_hash(pw_hash, password):
            return user

def identity(payload):
    user_id = payload['identity']
    user = models.User.query.filter_by(id=user_id).first()
    return user