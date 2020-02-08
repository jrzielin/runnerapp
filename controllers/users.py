from flask import Blueprint, jsonify, request
from app import db, models
from sqlalchemy.exc import IntegrityError
from helpers import parse_int
from constants import MAX_PAGE_SIZE, DEFAULT_PAGE, DEFAULT_PAGE_SIZE

users = Blueprint('users', __name__)

@users.route('/api/users', methods=['GET', 'POST'])
def user_list():
    if request.method == 'POST':
        user = models.User(
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=request.form.get('email'),
            password=request.form.get('password')
        )

        error = user.validate()

        if error:
            return jsonify({'error': error}), 400

        if models.User.query.filter_by(email=request.form.get('email')).first():
            return jsonify({'error': 'That email address is already in use'}), 400

        user.hash_password()
        
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.remove()
            return jsonify({'error': 'That email address is already in use'}), 400
        except:
            return jsonify({'error': 'Unable to create new user'}), 500

        return jsonify({'user': user.serialize()}), 201

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


@users.route('/api/users/<int:user_id>')
def user_detail(user_id):
    user = models.User.query.filter_by(id=user_id).first()

    if user is None:
        return jsonify({'error': 'User does not exist'}), 404
    
    return jsonify({'user': user.serialize()})


@users.route('/api/users/<int:user_id>/runs')
def user_runs(user_id):
    user = models.User.query.filter_by(id=user_id).first()

    if user is None:
        return jsonify({'error': 'User does not exist'}), 404

    return jsonify({'user': user.serialize(include_runs=True)})