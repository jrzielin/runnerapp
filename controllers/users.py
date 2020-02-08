from flask import jsonify, request, make_response
from flask_restful import Resource
from flask_jwt import jwt_required, current_identity
from app import db, models
from sqlalchemy.exc import IntegrityError
from helpers import parse_int, parse_bool
from constants import MAX_PAGE_SIZE, DEFAULT_PAGE, DEFAULT_PAGE_SIZE

class UserList(Resource):
    @jwt_required()
    def get(self):
        page = parse_int(request.args.get('page')) or DEFAULT_PAGE
        page_size = parse_int(request.args.get('page_size')) or DEFAULT_PAGE_SIZE
        search = request.args.get('search')

        if page_size > MAX_PAGE_SIZE:
            page_size = MAX_PAGE_SIZE

        if search:
            search = search.strip().split(' ')

            if len(search) > 1:
                first_name = search[0]
                last_name = search[1]
                users = models.User.query.filter_by(first_name=first_name, last_name=last_name).order_by('last_name').paginate(page, page_size, False).items
            else:
                first_name = search[0]
                users = models.User.query.filter_by(first_name=first_name).order_by('last_name').paginate(page, page_size, False).items
        else:
            users = models.User.query.order_by('last_name').paginate(page, page_size, False).items
        users = [user.serialize() for user in users]
        return jsonify({'users': users})

class Register(Resource):
    def post(self):
        user = models.User(
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=request.form.get('email'),
            password=request.form.get('password'),
            is_active=True,
            metric=parse_bool(request.form.get('metric', False))
        )

        error = user.validate()

        if error:
            return make_response(jsonify({'error': error}), 400)

        if models.User.query.filter_by(email=request.form.get('email')).first():
            return make_response(jsonify({'error': 'That email address is already in use'}), 400)

        user.hash_password()
        
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.remove()
            return make_response(jsonify({'error': 'That email address is already in use'}), 400)
        except:
            return make_response(jsonify({'error': 'Unable to create new user'}), 500)

        return jsonify({'user': user.serialize()}), 201

class UserDetail(Resource):
    @jwt_required()
    def get(self, user_id):
        user = models.User.query.filter_by(id=user_id).first()

        if user is None:
            return make_response(jsonify({'error': 'User does not exist'}), 404)
        
        return jsonify({'user': user.serialize()})

class UserRuns(Resource):
    @jwt_required()
    def get(self, user_id):
        user = models.User.query.filter_by(id=user_id).first()

        if user is None:
            return make_response(jsonify({'error': 'User does not exist'}), 404)

        return jsonify({'user': user.serialize(include_runs=True)})

class Profile(Resource):
    @jwt_required()
    def get(self):
        user = current_identity
        return jsonify({'user': user})

    @jwt_required()
    def put(self):
        user = current_identity
        
        if 'email' in request.form:
            if models.User.query.filter_by(email=request.form['email']).first():
                return make_response(jsonify({'error': 'That email address is already in use'}), 400)
            user.email = request.form['email']
        if 'password' in request.form:
            user.password = request.form['password']
        if 'first_name' in request.form:
            user.first_name = request.form['first_name']
        if 'last_name' in request.form:
            user.last_name = request.form['last_name']
        if 'metric' in request.form:
            user.metric = parse_bool(request.form['metric'])
        
        error = user.validate()
        if error:
            return make_response(jsonify({'error': error}), 400)

        try:
            db.session.commit()
        except:
            return make_response(jsonify({'error': 'Unable to update profile'}), 500)
        
        return jsonify({'user': user.serialize()})
    
    @jwt_required()
    def delete(self):
        user = current_identity
        user.is_active = False

        try:
            db.session.commit()
        except:
            return make_response(jsonify({'error': 'Unable to inactivate user'}), 500)

        return jsonify({'message': 'User inactivated'})