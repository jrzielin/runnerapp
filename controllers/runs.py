from flask import Blueprint, jsonify
import models

runs = Blueprint('runs', __name__)

@runs.route('/api/runs')
def run_list():
    runs = models.Run.query.all()
    return jsonify({'runs': runs})
