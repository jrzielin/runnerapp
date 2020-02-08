import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

import models
from controllers.runs import runs
from controllers.users import users

app.register_blueprint(runs)
app.register_blueprint(users)

if __name__ == '__main__':
    app.run()
