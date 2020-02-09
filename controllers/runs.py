from flask import jsonify, request, make_response
from flask_restful import Resource
from flask_jwt import jwt_required, current_identity
from sqlalchemy import desc
import models
from helpers import parse_date, parse_bool, parse_int
from app import db

class RunList(Resource):
    @jwt_required()
    def get(self):
        user_id = current_identity.id
        runs = models.Run.query.filter_by(user_id=user_id).order_by(desc('run_date'))
        runs = [run.serialize() for run in runs]
        return jsonify({'runs': runs})

    @jwt_required()
    def post(self):
        user_id = current_identity.id
        run = models.Run(
            user_id=user_id,
            run_date=parse_date(request.form.get('run_date')),
            distance=parse_int(request.form.get('distance')),
            duration=parse_int(request.form.get('duration')),
            metric=parse_bool(request.form.get('metric', current_identity.metric)),
            warmup=parse_int(request.form.get('warmup')),
            cooldown=parse_int(request.form.get('cooldown')),
            run_type=request.form.get('run_type'),
            location=request.form.get('location'),
            notes=request.form.get('notes')
        )

        error = run.validate()

        if error:
            return make_response(jsonify({'error': error}), 400)

        try:
            db.session.add(run)
            db.session.commit()
        except Exception as e:
            return make_response(jsonify({'error': 'Unable to create new run'}), 500)

        return make_response(jsonify({'run': run.serialize()}), 201)

class RunDetail(Resource):
    @staticmethod
    def get_run(run_id):
        return models.Run.query.filter_by(id=run_id).first()

    @staticmethod
    def send_404():
        return make_response(jsonify({'error': 'Run does not exist'}), 404)

    @staticmethod
    def send_403():
        return make_response(jsonify({'error': 'You are not authorized to update this record'}), 403)

    @jwt_required()
    def get(self, run_id):
        run = self.get_run(run_id)
        if not run:
            return self.send_404()
        
        return jsonify({'run': run.serialize(include_comments=True, include_intervals=True)})

    @jwt_required()
    def put(self, run_id):
        run = self.get_run(run_id)
        if not run:
            return self.send_404()

        if run.user_id != current_identity.id:
            return self.send_403()

        if 'run_date' in request.form:
            run.run_date = parse_date(request.form['run_date'])
        if 'distance' in request.form:
            run.distance = parse_int(request.form['distance'])
        if 'duration' in request.form:
            run.duration = parse_int(request.form['duration'])
        if 'metric' in request.form:
            run.metric = parse_bool(request.form['metric'])
        if 'warmup' in request.form:
            run.warmup = parse_int(request.form['warmup'])
        if 'cooldown' in request.form:
            run.cooldown = parse_int(request.form['cooldown'])
        if 'run_type' in request.form:
            run.run_type = request.form['run_type']
        if 'location' in request.form:
            run.location = request.form['location']
        if 'notes' in request.form:
            run.notes = request.form['notes']

        error = run.validate()

        if error:
            return make_response(jsonify({'error': error}), 400)

        try:
            db.session.commit()
        except:
            return make_response(jsonify({'error': 'Unable to update run'}), 500)
        
        return jsonify({'run': run.serialize()})
    
    @jwt_required()
    def delete(self, run_id):
        run = self.get_run(run_id)
        if not run:
            return self.send_404()
        
        if run.user_id != current_identity.id:
            return self.send_403()
        
        try:
            db.session.delete(run)
            db.session.commit()
        except:
            return make_response(jsonify({'error': 'Unable to delete run'}), 500)

        return jsonify({'message': 'Successfully deleted run'})

class CommentsList(Resource):
    @jwt_required()
    def get(self, run_id):
        run = models.Run.query.filter_by(id=run_id).first()
        if not run:
            return make_response(jsonify({'error': 'Run does not exist'}), 404)

        comments = [comment.serialize() for comment in run.run_comments]
        return jsonify({'comments': comments})
    
    @jwt_required()
    def post(self, run_id):
        run = models.Run.query.filter_by(id=run_id).first()
        if not run:
            return make_response(jsonify({'error': 'Run does not exist'}), 404)

        comment = models.RunComment(
            run_id=run_id,
            user_id=current_identity.id,
            comment=request.form.get('comment')
        )

        error = comment.validate()
        if error:
            return make_response(jsonify({'error': error}), 400)

        try:
            db.session.add(comment)
            db.session.commit()
        except:
            return make_response(jsonify({'error': 'Unable to add comment'}), 500)
        
        return jsonify({'comment': comment.serialize()})

class CommentDetail(Resource):
    @jwt_required()
    def get(self, comment_id):
        comment = models.RunComment.query.filter_by(id=comment_id).first()
        if comment is None:
            return make_response(jsonify({'error': 'Comment does not exist'}), 404)

        return jsonify({'comment': comment.serialize()})

    @jwt_required()
    def put(self, comment_id):
        comment = models.RunComment.query.filter_by(id=comment_id).first()
        if comment is None:
            return make_response(jsonify({'error': 'Comment does not exist'}), 404)

        if comment.user_id != current_identity.id:
            return make_response(jsonify({'error': 'Unauthorized to update comment'}), 403)

        if 'comment' in request.form:
            comment.comment = request.form['comment']

        error = comment.validate()
        if error:
            return make_response(jsonify({'error': error}), 400)
        
        try:
            db.session.commit()
        except:
            return make_response(jsonify({'error': 'Unable to update comment'}), 500)

        return jsonify({'comment': comment.serialize()})

    @jwt_required()
    def delete(self, comment_id):
        comment = models.RunComment.query.filter_by(id=comment_id).first()
        if comment is None:
            return make_response(jsonify({'error': 'Comment does not exist'}), 404)

        if comment.user_id != current_identity.id:
            return make_response(jsonify({'error': 'Unauthorized to update comment'}), 403)

        try:
            db.session.delete(comment)
            db.session.commit()
        except:
            return make_response(jsonify({'error': 'Unable to delete comment'}), 500)

        return jsonify({'message': 'Comment successfully deleted'})
