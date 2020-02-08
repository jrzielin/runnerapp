from flask import jsonify
from flask_restful import Resource
from flask_jwt import jwt_required, current_identity
import models

class RunList(Resource):
    @jwt_required()
    def get(self):
        runs = models.Run.query.all()
        return jsonify({'runs': runs})