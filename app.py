import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt import JWT
from flask_restful import Api
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
api = Api(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

import models
from auth import authenticate, identity

jwt = JWT(app, authenticate, identity)

from controllers.runs import RunList, RunDetail, CommentsList, CommentDetail
from controllers.users import Register, UserList, UserDetail, UserRuns, Profile

api.add_resource(Profile, '/api/profile')
api.add_resource(Register, '/api/register')
api.add_resource(UserList, '/api/users')
api.add_resource(UserDetail, '/api/users/<int:user_id>')
api.add_resource(UserRuns, '/api/users/<int:user_id>/runs')
api.add_resource(RunList, '/api/runs')
api.add_resource(RunDetail, '/api/runs/<int:run_id>')
api.add_resource(CommentsList, '/api/runs/<int:run_id>/comments')
api.add_resource(CommentDetail, '/api/comments/<int:comment_id>')

if __name__ == '__main__':
    app.run()
